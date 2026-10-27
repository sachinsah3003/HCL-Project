import re


def normalize_text(text):
    """
    Normalize text for searching and matching.
    This function does NOT remove stop words or lemmatize.
    """

    text = text.lower()

    text = text.replace("-", " ")
    text = text.replace("/", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()