import re


def clean_content(text: str) -> str:
    """Clean RSS content from parasitic images and links."""
    if not text:
        return ""

    text = re.sub(r"<img[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<a[^>]*>.*?</a>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]*>", "", text)

    text = re.sub(
        r"https?://[^\s]*\.(jpg|jpeg|png|gif|webp|svg)[^\s]*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(r"\[Image:.*?\]", "", text)
    text = re.sub(r"\(Image:.*?\)", "", text)
    text = re.sub(r"Image\s*:\s*[^\n]*", "", text, flags=re.IGNORECASE)

    text = re.sub(r"Read more.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Continue reading.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Source\s*:\s*.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Read full story.*", "", text, flags=re.IGNORECASE)

    text = re.sub(r"The post .* appeared first on.*", "", text)
    text = re.sub(r"Originally appeared on.*", "", text)

    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n+", " ", text)

    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"').replace("&apos;", "'")
    text = text.replace("\r", "").replace("\t", " ")

    text = re.sub(r"\[\s*\]", "", text)
    text = re.sub(r"\(\s*\)", "", text)

    return text.strip()
