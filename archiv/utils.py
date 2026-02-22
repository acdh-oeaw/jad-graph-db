import re

from openai import OpenAI

from archiv.models import TextSnippet

regex_patterns = [
    r"\([^)]*\)",  # remove everything between () including the parentheses
    r"\{[^}]*\}",  # remove everything between {} including the braces
    r"<[^>]*>",  # remove everything between <> including the brackets
    r"\d{2}\.\d{4}[A-Z]?\s?\|?",  # e.g. 92.0570C, 92.0570C |
    r"p\.\s*\d{4}[A-Z]?\s?\|?",  # e.g. p. 0570D |, p. 0581C |
    r"VERS\.\s*\d+\.\-\-",  # e.g. VERS. 4.--, VERS. 6.--
    r"\*",  # asterisk
    r"¶",  # pilcrow
    r"\[[^\]]*\]",  # anything in square brackets, including the brackets
    (r"» ", "»"),  # replace '» ' with '»',
    (r"« ", "«"),  # replace '« ' with '«',
    (r" \.", "."),  # remove space before period
    (r" ,", ","),  # remove space before comma
]


def clean_text(text):
    for pattern in regex_patterns:
        if isinstance(pattern, tuple):
            text = re.sub(pattern[0], pattern[1], text)
        else:
            text = re.sub(pattern, "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# Do not split after common abbreviations like 'etc.', 'e.g.', 'i.e.'
abbreviations = [
    "etc.",
    "e.g.",
    "i.e.",
    "cf.",
    "vs.",
    "dr.",
    "mr.",
    "mrs.",
    "ms.",
    "prof.",
    "inc.",
    "jr.",
    "sr.",
    "st.",
    "no.",
    "fig.",
    "al.",
    "ed.",
    "vol.",
    "pp.",
    "rev.",
]
# Build a regex negative lookbehind for these abbreviations
abbrev_regex = "|".join([re.escape(a) for a in abbreviations])
splitter_pattern = rf"(?<!\b(?:{abbrev_regex}))(?<=[.?!])\s+"


def sentence_splitter(text, splitter_pattern=splitter_pattern):
    cleaned = clean_text(text)
    # First split on sentence end
    sentences = re.split(r"(?<=[.?!])\s+", cleaned)
    # Then merge splits that happened after abbreviations
    merged = []
    for s in sentences:
        if merged and any(merged[-1].lower().endswith(abbr) for abbr in abbreviations):
            merged[-1] += " " + s
        else:
            merged.append(s)
    return [clean_text(s.strip()) for s in merged if s.strip()]


def vectorize(
    client: OpenAI,
    model_object: TextSnippet,
    vector_field: str = "embedding_nomic",
    embedding_model_name: str = "nomic-embed-text",
):
    if model_object.content:
        vector = (
            client.embeddings.create(
                input=[model_object.content],
                model=embedding_model_name,
            )
            .data[0]
            .embedding
        )
        setattr(model_object, vector_field, vector)
        model_object.save()
