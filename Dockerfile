# ============================================================
# CUDA 12.2 Runtime (Ubuntu 22.04)
# ============================================================
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# ============================================================
# System + build dependencies (KenLM / pyctcdecode safe)
# ============================================================
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3-dev \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    git \
    pkg-config \
    libboost-all-dev \
    portaudio19-dev \
    libasound-dev \
    libsndfile1 \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Make python3 default
RUN ln -sf /usr/bin/python3.10 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.10 /usr/bin/python

# ============================================================
# UTF-8 locale
# ============================================================
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# ============================================================
# Upgrade pip
# ============================================================
RUN python3 -m pip install --upgrade pip setuptools wheel

# ============================================================
# Install PyTorch (CUDA 12.x compatible wheels)
# ============================================================
RUN pip install torch==2.5.0 torchvision==0.20.0 torchaudio==2.5.0 \
    --index-url https://download.pytorch.org/whl/cu121

# ============================================================
# Working directory
# ============================================================
WORKDIR /app

# ============================================================
# Copy requirements first (better cache)
# ============================================================
COPY requirements.txt .

# ============================================================
# Install Python dependencies
# ============================================================
RUN pip install -r requirements.txt

# ============================================================
# Copy application code
# ============================================================
COPY . .

# ============================================================
# Hugging Face cache
# ============================================================
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface

# ============================================================
# Expose WebSocket port (matches your code)
# ============================================================
EXPOSE 11119

# ============================================================
# Start server
# ============================================================
CMD ["python3", "server.py"]