import re
from difflib import SequenceMatcher


def normalize_title(title: str) -> str:
    """Normalize title for duplicate comparison."""
    if not title:
        return ""

    normalized = title.lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
    }
    words = [w for w in normalized.split() if w not in stop_words and len(w) > 2]

    return " ".join(words)


def calculate_similarity(title1: str, title2: str) -> float:
    """Calculate similarity between two titles (0-1)."""
    norm1 = normalize_title(title1)
    norm2 = normalize_title(title2)

    if not norm1 or not norm2:
        return 0

    return SequenceMatcher(None, norm1, norm2).ratio()


def is_duplicate_article(
    article: dict, posted_titles: list, similarity_threshold: float = 0.75
) -> bool:
    """Check if article is duplicate of already posted article."""
    current_title = article["title"]

    for posted_title in posted_titles:
        similarity = calculate_similarity(current_title, posted_title)
        if similarity >= similarity_threshold:
            return True

    return False


def deduplicate_articles(
    articles: list, posted_titles: list, max_articles: int = 5
) -> list:
    """Remove duplicates from article list."""
    unique_articles = []
    seen_titles = []

    for article in articles:
        is_session_dup = False
        for seen_title in seen_titles:
            if calculate_similarity(article["title"], seen_title) >= 0.80:
                is_session_dup = True
                break

        if not is_session_dup and not is_duplicate_article(article, posted_titles):
            unique_articles.append(article)
            seen_titles.append(article["title"])

    return unique_articles[:max_articles]
