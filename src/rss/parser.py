import feedparser
from .cleaner import clean_content


def parse_feed(xml_content: str, source_name: str) -> list:
    """Parse RSS feed and return cleaned articles."""
    try:
        feed = feedparser.parse(xml_content)

        if not feed.entries:
            return []

        articles = []
        for entry in feed.entries[:3]:
            description = getattr(entry, "description", "")
            description = (
                description
                if isinstance(description, str)
                else str(description)
                if description
                else ""
            )

            description = clean_content(description)
            title = getattr(entry, "title", "Titre non disponible")

            if len(description.strip()) < 20 or "image" in title.lower():
                continue

            image_url = None
            if hasattr(entry, "enclosures") and entry.enclosures:
                for enclosure in entry.enclosures:
                    enc_type = (
                        enclosure.get("type", "") if isinstance(enclosure, dict) else ""
                    )
                    if enc_type.startswith("image/"):
                        image_url = enclosure.get("href") or enclosure.get("url")
                        break

            if (
                not image_url
                and hasattr(entry, "media_content")
                and entry.media_content
            ):
                for media in entry.media_content:
                    media_type = (
                        media.get("type", "") if isinstance(media, dict) else ""
                    )
                    if media_type.startswith("image/"):
                        image_url = media.get("url")
                        break

            if (
                not image_url
                and hasattr(entry, "media_thumbnail")
                and entry.media_thumbnail
            ):
                if (
                    isinstance(entry.media_thumbnail, list)
                    and len(entry.media_thumbnail) > 0
                ):
                    image_url = entry.media_thumbnail[0].get("url")

            article = {
                "title": title,
                "description": description,
                "link": getattr(entry, "link", ""),
                "pub_date": getattr(entry, "published", ""),
                "id": getattr(entry, "id", "") or getattr(entry, "link", ""),
                "source": source_name,
                "image_url": image_url,
            }
            articles.append(article)

        return articles

    except Exception:
        return []
