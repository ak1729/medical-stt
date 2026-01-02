import re

# Pre-compile regex patterns for better performance
COMPILED_PATTERNS = [
    (re.compile(r'\bbasal\s+systems?\b', re.IGNORECASE), 'basal cistern'),
    (re.compile(r'\bbessel\s+systems?\b', re.IGNORECASE), 'basal cistern'),
    (re.compile(r'\bbaffle\s+systems?\b', re.IGNORECASE), 'basal cistern'),
    (re.compile(r'\bbattle\s+systems?\b', re.IGNORECASE), 'basal cistern'),
    (re.compile(r'\bbafel\s+systems?\b', re.IGNORECASE), 'basal cistern'),
    (re.compile(r'\bbasel\s+systems?\b', re.IGNORECASE), 'basal cistern'),
    (re.compile(r'\bvessel\s+systems?\b', re.IGNORECASE), 'basal cistern'),
    (re.compile(r'\bbreach\s+systems?\b', re.IGNORECASE), 'basal cistern'),
    (re.compile(r'\bbasil\s+systems?\b', re.IGNORECASE), 'basal cistern'),
    (re.compile(r'\bbasic\s+systems?\b', re.IGNORECASE), 'basal cistern'),
    (re.compile(r'\bbase\s+systems?\b', re.IGNORECASE), 'basal cistern'),
    (re.compile(r'\bsuprasellar\s+systems?\b', re.IGNORECASE), 'suprasellar cistern'),
    (re.compile(r'\bquadrigeminal\s+systems?\b', re.IGNORECASE), 'quadrigeminal cistern'),
    (re.compile(r'\bambient\s+systems?\b', re.IGNORECASE), 'ambient cistern'),
    (re.compile(r'\bventricles\s+systems?\b', re.IGNORECASE), 'ventricular system'),
    
    (re.compile(r'(\d+)\s+by\s+(\d+)\s+by\s+(\d+)'), r'\1x\2x\3'),
    (re.compile(r'(\d+)\s+by\s+(\d+)'), r'\1x\2'),
    (re.compile(r'grams per centimeter square'), 'g/cm²'),
    (re.compile(r'\bdegree\b'), '°C'),
    (re.compile(r'\bdegrees\b'), '°C'),
    (re.compile(r'^[,.]+'), ''),
    (re.compile(r'\bcolon\b'), ': '),
    (re.compile(r'\bcolumn\b'), ': '),
    (re.compile(r'\bcolony\b'), ': '),
    (re.compile(r'(?i)new\s*line'), '<br>'),
    (re.compile(r'(?i)new\s*lane'), '<br>'),
    (re.compile(r'(?i)new\s*time'), '<br>'),
    (re.compile(r'(?i)new\s*link'), '<br>'),
    (re.compile(r'(?i)change\s*para'), '<br><br>'),
    (re.compile(r'(?i)change\s*pera'), '<br><br>'),
    (re.compile(r'(?i)neck\s*line'), '<br>'),
    (re.compile(r'(?i)neck\s*lane'), '<br>'),
    (re.compile(r'(?i)next\s*line'), '<br>'),
    (re.compile(r'(?i)next\s*time'), '<br>'),
    (re.compile(r'(?i)next\s*land'), '<br>'),
    (re.compile(r'(?i)\bnext\s*link\b'), '<br>'),
    (re.compile(r'(?i)\bnext\s*slide\b'), '<br>'),
    (re.compile(r'(?i)\bnext\s*side\b'), '<br>'),
    (re.compile(r'\blane\b'), '<br>'),
    (re.compile(r'\bBeeline\b'), '<br>'),
    (re.compile(r'\bonline\b'), '<br>'),
    (re.compile(r'\bOnline\b'), '<br>'),
    (re.compile(r'(?i)open\s*bracket'), '['),
    (re.compile(r'(?i)open\s*brackets'), '['),
    (re.compile(r'(?i)close\s*bracket'), ']'),
    (re.compile(r'(?i)close\s*brackets'), ']'),
    (re.compile(r'\bbracket\b'), ' []'),
    (re.compile(r'\bbrackets\b'), ' []'),
    (re.compile(r'\bbreak it\b'), ' []'),
    (re.compile(r'\blink\b'), '<br>'),
    (re.compile(r'\bperiod\b'), '. '),
    (re.compile(r'\bpoints\b'), '.'),
    (re.compile(r'\bpoint\b'), '.'),
    (re.compile(r'\bperiods\b'), '.'),
    (re.compile(r'\bcentimeters|centimetres\b'), 'cm'),
    (re.compile(r'\bperiod\s*\.\s*'), '. '),
    (re.compile(r'\bsemi\b'), '; '),
    (re.compile(r'\bcrore\b'), 'X'),
    (re.compile(r'\bcrores\b'), 'X'),
    (re.compile(r'\bcross\b'), 'X'),
    (re.compile(r'\bsoap\b'), 'soft'),
    (re.compile(r'\bbullet\b'), '•'),
    (re.compile(r'\bbullets\b'), '•'),
    (re.compile(r'\bfull stop\b'), '.'),
    (re.compile(r'\bhyphen\b'), ' - '),
    (re.compile(r'\bhypen\b'), ' - '),
    (re.compile(r'hyphen'), ' - '),
    (re.compile(r'hypen'), ' - '),
    # (re.compile(r'hype'), ' - '),
    (re.compile(r'\b(ct|MDCT|acl|pcl|mcl)\b'), lambda x: x.group(0).upper()),
    (re.compile(r'\btechnical\b'), 'Technical'),
    (re.compile(r'\btechniques\b'), 'Technical'),
    (re.compile(r'\btechniquesal\b'), 'Technical'),
    (re.compile(r'\bm(l|L)\b'), 'mL'),
    (re.compile(r'\bmillimeter\b'), 'mm'),
    (re.compile(r'\bmca\b'), 'MCA'),
    (re.compile(r'\b(cp|Cd)\b'), 'CT'),
    (re.compile(r'\bcity\b'), 'CT'),
    (re.compile(r'\bmarigold\b'), 'malignant'),
    (re.compile(r'\bparenkima\b'), 'paranchyma'),
    (re.compile(r'\btoyota\b'), 'aorta'),
    (re.compile(r'two'), '2'),
    (re.compile(r'\btwo\b'), '2'),
    (re.compile(r'\btwo'), '2'),
    (re.compile(r'\bperiod\s+\.\s*'), '. '),
    (re.compile(r'\bayy?ota\b'), 'Aorta'),
    (re.compile(r'\biota\b'), 'aorta'),
    (re.compile(r'\b(p|P)am\b'), 'Palm'),
    (re.compile(r'\bscene\b'), 'seen'),
    (re.compile(r'\btbl\b'), 'tibia'),
    (re.compile(r'\bni\b'), 'knee'),
    (re.compile(r'\b(mdcd|mdct|empty\sCT)\b'), 'MDCT'),
    (re.compile(r'\bmsct\b'), 'MSCT'),
    (re.compile(r'\bmsct'), 'MSCT'),
    (re.compile(r'msct\b'), 'MSCT'),
    (re.compile(r'\bOPEC\b'), 'opaque'),
    (re.compile(r'\disk\b'), 'disc'),
    (re.compile(r'msct'), 'MSCT'),
    (re.compile(r'\bth\b'), 'TH'),
    (re.compile(r'\blb\b'), 'LB'),
    (re.compile(r'\bcsf\b'), 'CSF'),
    (re.compile(r'\bsoftware\b'), 'soft'),
    (re.compile(r'\bnick\b'), 'neck'),
    (re.compile(r'\bexclamation\b'), '!'),
    (re.compile(r'\bslash\b'), '/'),
    (re.compile(r'\bsemicolon\b'), '; '),
    (re.compile(r'\bsemi colon\b'), '; '),
    (re.compile(r'\bspace\b'), ' '),
    (re.compile(r'(?<=\s)-:'), ''),
    (re.compile(r'\s+'), ' '),
    (re.compile(r'(\w)\s*\.\s+(?=\w)'), r'\1. '),
    (re.compile(r'\bl([1-5])'), r'L\1'),
    (re.compile(r'\bc([1-7])'), r'C\1'),
    (re.compile(r'\bt([1-9]|1[0-2])'), r'T\1'),
    (re.compile(r'\bs([1-5])'), r'S\1'),
]

# Pre-compiled regex patterns for common operations
WORD_PATTERN = re.compile(r'\w+|[^\w\s]')
WHITESPACE_PATTERN = re.compile(r'\s+')
SENTENCE_SPLIT_PATTERN = re.compile(r'(?<=[.:!?])\s*')
BR_CAPITALIZE_PATTERN = re.compile(r'(?i)(<br>\s*)(\w)')

# Pre-defined dictionaries
NUMWORDS = {}
def _init_numwords():
    global NUMWORDS
    if NUMWORDS:  # Already initialized
        return

    units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
    ]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    scales = ["hundred", "thousand", "million", "billion", "trillion"]

    for idx, word in enumerate(units):
        NUMWORDS[word] = (1, idx)
    for idx, word in enumerate(tens):
        NUMWORDS[word] = (1, idx * 10)
    for idx, word in enumerate(scales):
        NUMWORDS[word] = (10 ** (idx * 3 or 2), 0)

# Initialize numwords dictionary once
_init_numwords()

# Pre-defined dictionaries for faster lookups
ORDINAL_WORDS = {'first': 1, 'second': 2, 'third': 3, 'fifth': 5, 'eighth': 8, 'ninth': 9, 'twelfth': 12}
ORDINAL_ENDINGS = [('ieth', 'y'), ('tieth', 'ty')]
ORDINAL_TENS = {'twentieth': 20, 'thirtieth': 30, 'fortieth': 40, 'fiftieth': 50,
                'sixtieth': 60, 'seventieth': 70, 'eightieth': 80, 'ninetieth': 90}

CORRECTOR = {'!': '', '?': '', ',': ''}
NUM_CORRECTOR = {'first': '1st', 'second': '2nd', 'third': '3rd', 'fourth': '4th', 'fifth': '5th',
                 'sixth': '6th', 'seventh': '7th', 'eightth': '8th', 'ninth': '9th'}

FORMATTING_TAGS = {
    "underline": "u",
    "underlined": "u",
    "bold": "strong",
    "italic": "em",
}

SPECIAL_FORMATTING = {
    "heading": lambda x: f'<strong style="font-size: 20px;">{x}</strong>',
    "title": lambda x: f'<strong style="font-size: 24px;"><u>{x}<u></strong>',
    "subtitle": lambda x: f'<strong style="font-size: 14px;"><u>{x}<u></strong>',
}

CHECK_CHARACTERS = {',', ':', '!', '.', '?'}

def text2int(textnum):
    """Optimized text to integer conversion"""
    current = result = 0
    curstring = ""
    onnumber = False

    # Use str.translate for faster character replacement
    textnum = textnum.replace('-', ' ')

    for word in textnum.split():
        if word in ORDINAL_TENS:
            curstring += str(ORDINAL_TENS[word]) + 'th '
            onnumber = False
        elif word in ORDINAL_WORDS:
            scale, increment = (1, ORDINAL_WORDS[word])
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0
            onnumber = True
        else:
            # Check ordinal endings
            for ending, replacement in ORDINAL_ENDINGS:
                if word.endswith(ending):
                    word = word[:-len(ending)] + replacement
                    break

            if word not in NUMWORDS:
                if onnumber:
                    curstring += str(result + current) + " "
                curstring += word + " "
                result = current = 0
                onnumber = False
            else:
                scale, increment = NUMWORDS[word]
                current = current * scale + increment
                if scale > 100:
                    result += current
                    current = 0
                onnumber = True

    if onnumber:
        curstring += str(result + current)

    return curstring

def format_sentence(sentence):
    """Optimized sentence formatting"""
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

def convert_measurement(text):
    """Optimized measurement conversion with pre-compiled patterns"""
    # Fast character replacement using translate
    for char, replacement in CORRECTOR.items():
        text = text.replace(char, replacement)

    for char, replacement in NUM_CORRECTOR.items():
        text = text.replace(char, replacement)

    # Convert textual numbers to integers
    text = text2int(text)

    # Remove extra spaces
    text = WHITESPACE_PATTERN.sub(' ', text)
    text = format_sentence(text)

    # Apply all pre-compiled patterns
    for pattern, replacement in COMPILED_PATTERNS:
        text = pattern.sub(replacement, text)

    # Split text into sentences and capitalize
    sentences = SENTENCE_SPLIT_PATTERN.split(text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Capitalize sentences efficiently
    capitalized_sentences = []
    for sentence in sentences:
        if sentence:
            capitalized_sentences.append(sentence[0].upper() + sentence[1:])

    capitalized_text = ' '.join(capitalized_sentences)

    # Correct capitalization after <br>
    capitalized_text = BR_CAPITALIZE_PATTERN.sub(
        lambda match: match.group(1) + match.group(2).capitalize(),
        capitalized_text
    )

    # Remove unwanted space before punctuation using list comprehension
    text_chars = list(capitalized_text)
    for i in range(1, len(text_chars)):
        if text_chars[i] in CHECK_CHARACTERS and text_chars[i - 1] == ' ':
            text_chars[i - 1] = ''

    return ''.join(text_chars)