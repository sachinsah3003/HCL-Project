import re

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from src.utils.helpers import normalize_text

stop_words = set(stopwords.words("english"))

lemmatizer = WordNetLemmatizer()


def preprocess_text(text):
    """
    Clean and normalize text before TF-IDF vectorization.
    """

    # Reuse shared text normalization before token-level cleanup.
    text = normalize_text(text)

    # Remove unnecessary punctuation
    text = re.sub(r"[^\w\s.+#]", " ", text)

    # Split text into individual tokens
    tokens = text.split()

    # Remove stop words and lemmatize tokens
    processed_tokens = []

    for token in tokens:
        if token not in stop_words:
            lemma = lemmatizer.lemmatize(token)
            processed_tokens.append(lemma)

    # Join processed tokens back into text
    processed_text = " ".join(processed_tokens)

    return processed_text