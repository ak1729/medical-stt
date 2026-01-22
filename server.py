import asyncio
import base64
import datetime
import gc
import json
import uuid
import logging
import sys
import numpy as np
import pyaudio
import torch
import websockets
from silero_vad import get_speech_timestamps, load_silero_vad
import dataclasses
import pyctcdecode
import transformers
import huggingface_hub

from text_processing import *

# from huggingface_hub import login
# login()

# ---------------------------------------------------
# LOGGING (BASIC)
# ---------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

vad_model = load_silero_vad()

# Audio parameters
CHANNELS = 1
RATE = 16000

MAX_CONCURRENT_TRANSCRIPTIONS = 30
transcribe_semaphore = asyncio.Semaphore(MAX_CONCURRENT_TRANSCRIPTIONS)
transcription_queue = asyncio.Queue()

model_id = "google/medasr"

def _restore_text(text: str) -> str:
  return text.replace(" ", "").replace("#", " ").replace(".</s>", "").replace(". </s>", "").replace("</s>", "").replace("]", "").replace("[", "").strip()


class LasrCtcBeamSearchDecoder:

  def __init__(
      self,
      tokenizer: transformers.LasrTokenizer,
      kenlm_model_path=None,
      **kwargs,
  ):
    vocab = [None for _ in range(tokenizer.vocab_size)]
    for k, v in tokenizer.vocab.items():
      if v < tokenizer.vocab_size:
        vocab[v] = k
    assert not [i for i in vocab if i is None]
    vocab[0] = ""
    for i in range(1, len(vocab)):
      piece = vocab[i]
      if not piece.startswith("<") and not piece.endswith(">"):
        piece = "▁" + piece.replace("▁", "#")
      vocab[i] = piece
    self._decoder = pyctcdecode.build_ctcdecoder(
        vocab, kenlm_model_path, **kwargs
    )

  def decode_beams(self, *args, **kwargs):
    beams = self._decoder.decode_beams(*args, **kwargs)
    return [dataclasses.replace(i, text=_restore_text(i.text)) for i in beams]


def beam_search_pipe(model: str, lm: str):
  feature_extractor = transformers.LasrFeatureExtractor.from_pretrained(model)
  feature_extractor._processor_class = "LasrProcessorWithLM"
  pipe = transformers.pipeline(
      task="automatic-speech-recognition",
      model=model,
      feature_extractor=feature_extractor,
      decoder=LasrCtcBeamSearchDecoder(
          transformers.AutoTokenizer.from_pretrained(model), lm
      ),
  )
  assert pipe.type == "ctc_with_lm"
  return pipe

pipe_with_lm = beam_search_pipe(
    model_id,
    huggingface_hub.hf_hub_download(model_id, filename='lm_6.kenlm'),
)

audio = pyaudio.PyAudio()

# Client tracking dictionary
client_map = {}  # Maps client_id -> {"websocket": ws, "last_ended_with_delimiter": bool}

# Silence detection parameters
MIN_SILENCE_LENGTH = 0.8
MIN_AUDIO_DURATION = 2.0
MAX_SILENCE_BUFFER = 5.0

# Remove initial samples
samples_to_remove = 44
sample_width = 2
bytes_to_remove = samples_to_remove * sample_width


def audio_bytes_to_array(audio_bytes, channels=CHANNELS, sample_width=2, sample_rate=RATE):
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
    audio_np = audio_np / 32768.0
    return audio_np


async def safe_ws_send(ws, message, timeout=4.0):
    try:
        await asyncio.wait_for(ws.send(message), timeout=timeout)
        return True
    except asyncio.TimeoutError:
        logger.warning("WebSocket send timeout")
        return False
    except websockets.exceptions.ConnectionClosed:
        logger.warning("WebSocket already closed")
        return False
    except Exception as e:
        logger.error(f"Unexpected send error: {e}", exc_info=True)
        return False


async def receive_and_write_audio(websocket):
    client_id = str(uuid.uuid4())
    client_map[client_id] = {
        "websocket": websocket,
        "buffer": b"",
        "last_active": datetime.datetime.utcnow(),
        "last_speech_time": None,
        "last_ended_with_delimiter": False,
    }
    logger.info(f"React client connected: {client_id}")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                client_map[client_id]["last_active"] = datetime.datetime.utcnow()

                if "audio" in data:
                    audio_data = base64.b64decode(data["audio"])
                    cleaned_audio = (
                        audio_data[bytes_to_remove:]
                        if len(audio_data) > bytes_to_remove
                        else audio_data
                    )
                    client_map[client_id]["buffer"] += cleaned_audio
                    buffer = client_map[client_id]["buffer"]
                    buffer_duration_seconds = len(buffer) / RATE / 2
                    audio_array = (
                        np.frombuffer(buffer, dtype=np.int16).astype(np.float32)
                        / 32768.0
                    )

                    speech_timestamps = get_speech_timestamps(
                        audio_array, vad_model, sampling_rate=RATE
                    )

                    if speech_timestamps:
                        logger.info(f"speech timestamp detected")
                        client_map[client_id]["last_speech_time"] = datetime.datetime.utcnow()
                        # client_map[client_id]["buffer"] += cleaned_audio
                        last_speech_end = speech_timestamps[-1]["end"] / RATE
                        buffer_duration = len(buffer) / RATE / 2
                        silence_duration = buffer_duration - last_speech_end

                        if buffer_duration < MIN_AUDIO_DURATION:
                            status = "unconfirmed"
                        else:
                            status = (
                                "confirmed"
                                if silence_duration >= MIN_SILENCE_LENGTH
                                else "unconfirmed"
                            )

                        await transcription_queue.put(
                            (client_id, buffer, status, silence_duration)
                        )

                        if status == "confirmed":
                            end_index = int(speech_timestamps[-1]["end"] * 2)
                            client_map[client_id]["buffer"] = (
                                buffer[end_index:] if end_index < len(buffer) else b""
                            )

                    else:
                        last_speech = client_map[client_id].get("last_speech_time")
                        current_time = datetime.datetime.utcnow()

                        if last_speech:
                            silence_since_speech = (current_time - last_speech).total_seconds()
                        else:
                            silence_since_speech = buffer_duration_seconds

                        if silence_since_speech > MAX_SILENCE_BUFFER:
                            logger.info(f"Clearing buffer due to prolonged silence ({silence_since_speech:.2f}s)")
                            client_map[client_id]["buffer"] = b""
                            client_map[client_id]["last_speech_time"] = None
                            
                        ws = client_map[client_id]["websocket"]
                        response = json.dumps({"status": "unconfirmed", "transcription": ""})
                        await safe_ws_send(ws, response)

            except json.JSONDecodeError:
                logger.warning("Received non-JSON message")
            except Exception as e:
                logger.error(f"Error in client loop: {e}", exc_info=True)

    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"Client {client_id} disconnected with error: {e}", exc_info=True)

    finally:
        if client_id in client_map:
            del client_map[client_id]
            logger.info(f"Cleaned client {client_id} (Total clients: {len(client_map)})")


async def transcribe_and_send(client_id, audio_bytes, status, silence_duration):
    try:
        # await asyncio.sleep(0.1)
        audio_array = audio_bytes_to_array(audio_bytes)

        result = pipe_with_lm(audio_array, chunk_length_s=20, stride_length_s=2, decoder_kwargs=dict(beam_width=8))
        transcript = result["text"]
        text_ = ""
        if transcript:

            if status == "confirmed":
                text_ = transcript.strip()
                logger.info(f"original text: {text_}")
                prev_delimiter = client_map[client_id].get("last_ended_with_delimiter", False)
                text_, ends_with_delimiter = text_post_processing(text_, previous_ended_with_delimiter=prev_delimiter)
                client_map[client_id]["last_ended_with_delimiter"] = ends_with_delimiter
                logger.info(f"corrected text: {text_}")

            else:
                text_ = transcript

        if client_id in client_map:
            ws = client_map[client_id]["websocket"]
            response = json.dumps({"status": status, "transcription": text_})

            sent = await safe_ws_send(ws, response)
            if not sent:
                if client_id in client_map:
                    del client_map[client_id]
                    logger.warning(f"Removed client {client_id} after failed send")

    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        if client_id in client_map:
            await safe_ws_send(
                client_map[client_id]["websocket"],
                json.dumps({"error": "Transcription failed"}),
            )

    finally:
        pass


async def transcription_worker():
    logger.info("Transcription worker started.")
    while True:
        client_id, audio_bytes, status, silence_duration = await transcription_queue.get()
        try:
            async with transcribe_semaphore:
                if client_id in client_map:
                    await transcribe_and_send(client_id, audio_bytes, status, silence_duration)
        except Exception as e:
            logger.error(f"Worker error: {e}", exc_info=True)
        finally:
            transcription_queue.task_done()


async def cleanup_idle_clients(timeout_seconds=60):
    while True:
        now = datetime.datetime.utcnow()
        for cid, entry in list(client_map.items()):
            if (now - entry.get("last_active", now)).total_seconds() > timeout_seconds:
                logger.info(f"Cleaning idle client {cid}")
                try:
                    await entry["websocket"].close()
                except Exception:
                    pass
                client_map.pop(cid, None)
        await asyncio.sleep(10)


async def cleanup_gpu_memory(interval_seconds=180):
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            torch.cuda.synchronize()
            gc.collect()
            torch.cuda.empty_cache()
            logger.info(f"[{datetime.datetime.utcnow()}] GPU & GC cleanup done.")
        except Exception as e:
            logger.error(f"GPU cleanup error: {e}", exc_info=True)


async def start_server():
    server = await websockets.serve(receive_and_write_audio, "0.0.0.0", 11119)
    logger.info("WebSocket server started on ws://0.0.0.0:11119")

    asyncio.create_task(transcription_worker())
    asyncio.create_task(cleanup_idle_clients())
    asyncio.create_task(cleanup_gpu_memory())

    await server.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(start_server())
    except KeyboardInterrupt:
        logger.warning("SERVER STOPPED via KeyboardInterrupt.")
    finally:
        audio.terminate()
