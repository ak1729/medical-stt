import re

def text_post_processing(text: str) -> str:
    replacements = {
        "{period}": ".",
        "{comma}": ",",
        "{colon}": ":",
        "{semicolon}": ";",
        "{question mark}": "?",
        "{slash}": "/",
        "{hyphen}": "-",
        "{dash}": "-",
        "{newline}": "<br>",
        "{new line}": "<br>",
        "{new paragraph}": "<br><br>",
        "{tab}": "     ",
        "{start}": "",
        "{end}": "",
        "{bracket}": "[]",
        "{[]}": "[]",
        "{open parenthesis}": "(",
        "{close parenthesis}": ")",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    # {caps} nextword → NEXTWORD
    text = re.sub(r"\{caps\}\s+(\w+)", lambda m: m.group(1).upper(), text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)

    return text.strip()
