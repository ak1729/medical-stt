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
    "{new paragraph}": "<br><br>",
    "{open parenthesis}": "(",
    "{close parenthesis}": ")"
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
CAPS_PATTERN = re.compile(r"\{caps\}\s+(\w+)", re.IGNORECASE)
CURLY_PATTERN = re.compile(r"[{}]")
WHITESPACE_PATTERN = re.compile(r"\s+")
PUNCTUATION_PATTERN = re.compile(r"[,?!:;/]")
REPLACEMENT_PATTERN = re.compile("|".join(re.escape(k) for k in sorted(REPLACEMENTS, key=len, reverse=True)))
NUMBER_PATTERN = re.compile(r"\b(" + "|".join(NUMBER_WORDS.keys()) + r")\b", re.IGNORECASE)
ORDINAL_PATTERN = re.compile(r"\b(" + "|".join(ORDINAL_WORDS.keys()) + r")\b", re.IGNORECASE)

# ---------Formatting Tags---------
FORMATTING_TAGS = {
    "underline": "u",
    "bold": "strong",
    "italic": "em",
}
SPECIAL_FORMATTING = {
    "heading": lambda x: f'<strong style="font-size: 20px;">{x}</strong>',
    "title": lambda x: f'<strong style="font-size: 24px;"><u>{x}<u></strong>',
    "subtitle": lambda x: f'<strong style="font-size: 16px;"><u>{x}<u></strong>',
}


def format_sentence(sentence):
    words = WORD_PATTERN.findall(sentence)

    result = []
    formatting = set()
    paragraph_mode = False
    special_modes = set()
    formatted_content = []

    def apply_formatting(text):
        for fmt in formatting:
            text = f"<{fmt}>{text}</{fmt}>"
        for mode in special_modes:
            if mode in SPECIAL_FORMATTING:
                text = SPECIAL_FORMATTING[mode](text)
        return text

    for word in words:
        word_lower = word.lower()
        if word_lower in FORMATTING_TAGS:
            formatting.add(FORMATTING_TAGS[word_lower])
        elif word_lower in SPECIAL_FORMATTING:
            special_modes.add(word_lower)
        elif word_lower == "paragraph":
            paragraph_mode = True
            formatted_content = []
        elif word_lower == "<br>":
            if paragraph_mode or special_modes:
                result.append(apply_formatting(" ".join(formatted_content)))
                result.append(word)
                formatting = set()
                special_modes = set()
                paragraph_mode = False
                formatted_content = []
            else:
                result.append(word)
        else:
            if paragraph_mode or special_modes:
                formatted_content.append(word)
            elif formatting:
                result.append(apply_formatting(word))
                formatting = set()
            else:
                result.append(word)

    if (paragraph_mode or special_modes) and (formatting or special_modes):
        result.append(apply_formatting(" ".join(formatted_content)))

    return " ".join(result)


def text_post_processing(text: str) -> str:
    text = PUNCTUATION_PATTERN.sub("", text)
    text = REPLACEMENT_PATTERN.sub(lambda m: REPLACEMENTS[m.group(0)], text)
    text = CAPS_PATTERN.sub(lambda m: m.group(1).upper(), text)
    text = CURLY_PATTERN.sub(" ", text)
    text = WHITESPACE_PATTERN.sub(" ", text).strip()
    text = ORDINAL_PATTERN.sub(lambda m: ORDINAL_WORDS[m.group(1).lower()], text)
    text = NUMBER_PATTERN.sub(lambda m: NUMBER_WORDS[m.group(1).lower()], text)

    return format_sentence(text)
