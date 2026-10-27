from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sentence_transformers import util


@lru_cache(maxsize=1)
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def calculate_semantic_similarity(text1, text2):
    if not text1.strip() or not text2.strip():
        return 0.0

    model = load_model()

    embeddings = model.encode(
        [text1, text2],
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    similarity = util.cos_sim(
        embeddings[0],
        embeddings[1],
    ).item()

    # Convert cosine similarity into a 0–100 score.
    score = max(0.0, min(1.0, similarity)) * 100

    return round(score, 2)
