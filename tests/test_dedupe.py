import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.deduplication.dedupe import (
    normalize_title,
    calculate_similarity,
    is_duplicate_article,
    deduplicate_articles,
)


def test_normalize_title():
    assert normalize_title("Bitcoin Surges to $100K!") == "bitcoin surges 100k"
    assert normalize_title("The Ethereum Upgrade is Here") == "ethereum upgrade here"
    assert normalize_title("") == ""


def test_calculate_similarity():
    s1 = calculate_similarity("Bitcoin hits new high", "Bitcoin hits new high")
    assert s1 == 1.0

    s2 = calculate_similarity("Bitcoin price rises", "Bitcoin price falls")
    assert 0.5 < s2 < 1.0

    s3 = calculate_similarity("Bitcoin", "Ethereum")
    assert s3 < 0.5


def test_is_duplicate_article():
    article = {"title": "Bitcoin Reaches $100K"}
    posted = ["Bitcoin hits $100K"]

    assert is_duplicate_article(article, posted, 0.75) == True

    article2 = {"title": "Ethereum launches new feature"}
    assert is_duplicate_article(article2, posted, 0.75) == False


def test_deduplicate_articles():
    articles = [
        {"title": "Bitcoin", "id": "1"},
        {"title": "Bitcoin", "id": "2"},  # duplicate
        {"title": "Ethereum", "id": "3"},
    ]
    posted = []

    result = deduplicate_articles(articles, posted, max_articles=5)
    assert len(result) == 2
