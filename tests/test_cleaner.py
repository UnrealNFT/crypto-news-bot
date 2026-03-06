import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rss.cleaner import clean_content


def test_clean_html_tags():
    html = "<p>Hello <b>World</b></p>"
    assert clean_content(html) == "Hello World"


def test_clean_images():
    text = "Check this image: <img src='test.jpg'> and read more"
    result = clean_content(text)
    assert "img" not in result.lower()


def test_clean_links():
    text = "Visit <a href='https://example.com'>our site</a> for more"
    result = clean_content(text)
    assert "href" not in result


def test_clean_html_entities():
    text = "Test &amp; &lt; &gt; &quot;"
    result = clean_content(text)
    assert "&amp;" not in result
    assert "&lt;" not in result


def test_clean_read_more():
    text = "Article content Read more at source"
    result = clean_content(text)
    assert "Read more" not in result


def test_empty_input():
    assert clean_content("") == ""
    assert clean_content(None) == ""
