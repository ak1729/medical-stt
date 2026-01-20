import re

REPLACEMENTS = {
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
    "{next line}": "<br>",
    "{new paragraph}": "<br><br>",
    "{new para}": "<br><br>",
    "{next paragraph}": "<br><br>",
    "{next para}": "<br><br>",
    "{open parenthesis}": "(",
    "{close parenthesis}": ")",
}

# --------Number Normalization--------
NUMBER_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
}

ORDINAL_WORDS = {
    "first": "1st",
    "second": "2nd",
    "third": "3rd",
    "fourth": "4th",
    "fifth": "5th",
    "sixth": "6th",
    "seventh": "7th",
    "eighth": "8th",
    "ninth": "9th",
    "tenth": "10th",
    "eleventh": "11th",
    "twelfth": "12th",
    "thirteenth": "13th",
    "fourteenth": "14th",
    "fifteenth": "15th",
    "sixteenth": "16th",
    "seventeenth": "17th",
    "eighteenth": "18th",
    "nineteenth": "19th",
    "twentieth": "20th",
}


# --------Regex Pattern--------
WORD_PATTERN = re.compile(r"<br>|\w+|[^\w\s]")
CAPS_PATTERN = re.compile(r"(?:\{?\b(?:capitalized|capitalize|caps)\b\}?)\s+(.*?)(?=<br>|$)", re.IGNORECASE)
BOLD_PATTERN = re.compile(r"(?:\{?\b(?:bold)\b\}?(?:\s+paragraph)?)\s+(.*?)(?=<br>|$)", re.IGNORECASE)
UNDERLINE_PATTERN = re.compile(r"(?:\{?\b(?:underline)\b\}?(?:\s+paragraph)?)\s+(.*?)(?=<br>|$)", re.IGNORECASE)
HEADING_PATTERN = re.compile(r"(?:\{?\b(?:heading)\b\}?)\s+(.*?)(?=<br>|$)", re.IGNORECASE)
TITLE_PATTERN = re.compile(r"(?:\{?\b(?:title)\b\}?)\s+(.*?)(?=<br>|$)", re.IGNORECASE)
SUBTITLE_PATTERN = re.compile(r"(?:\{?\b(?:subtitle)\b\}?)\s+(.*?)(?=<br>|$)", re.IGNORECASE)
CURLY_PATTERN = re.compile(r"[{}]")
WHITESPACE_PATTERN = re.compile(r"\s+")
PUNCTUATION_PATTERN = re.compile(r"[.,?!:;/]")
REPLACEMENT_PATTERN = re.compile("|".join(re.escape(k) for k in sorted(REPLACEMENTS, key=len, reverse=True)))
NUMBER_PATTERN = re.compile(r"\b(" + "|".join(NUMBER_WORDS.keys()) + r")\b", re.IGNORECASE)
ORDINAL_PATTERN = re.compile(r"\b(" + "|".join(ORDINAL_WORDS.keys()) + r")\b", re.IGNORECASE)


def text_post_processing(text: str) -> str:
    text = PUNCTUATION_PATTERN.sub("", text)
    text = REPLACEMENT_PATTERN.sub(lambda m: REPLACEMENTS[m.group(0)], text)
    text = CAPS_PATTERN.sub(lambda m: m.group(1).upper(), text)
    text = CURLY_PATTERN.sub(" ", text)
    text = HEADING_PATTERN.sub(lambda m: f'''<strong style="font-size: 20px;">{m.group(1)[0].upper() + m.group(1)[1:]}</strong>''', text)
    text = TITLE_PATTERN.sub(lambda m: f'''<strong style="font-size: 24px;"><u>{m.group(1)[0].upper() + m.group(1)[1:]}</u></strong>''', text)
    text = SUBTITLE_PATTERN.sub(lambda m: f'''<strong style="font-size: 16px;"><u>{m.group(1)[0].upper() + m.group(1)[1:]}</u></strong>''', text)
    text = BOLD_PATTERN.sub(lambda m: f"<strong>{m.group(1)}</strong>", text)
    text = UNDERLINE_PATTERN.sub(lambda m: f"<u>{m.group(1)}</u>", text)
    text = WHITESPACE_PATTERN.sub(" ", text).strip()
    text = ORDINAL_PATTERN.sub(lambda m: ORDINAL_WORDS[m.group(1).lower()], text)
    text = NUMBER_PATTERN.sub(lambda m: NUMBER_WORDS[m.group(1).lower()], text)
    
    return text
