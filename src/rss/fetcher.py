import requests
from .parser import parse_feed


NEWS_SOURCES = [
    {
        "name": "CoinTelegraph",
        "rss": "https://cointelegraph.com/rss",
        "use_proxy": True,
    },
    {
        "name": "CoinDesk",
        "rss": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "use_proxy": True,
    },
    {
        "name": "CryptoNews",
        "rss": "https://cryptonews.com/news/feed/",
        "use_proxy": False,
    },
]

CORS_PROXIES = [
    "https://api.codetabs.com/v1/proxy?quest=",
    "https://corsproxy.github.io/?",
    "https://proxy.cors.sh/",
    "https://api.allorigins.win/raw?url=",
]


def fetch_news(logger=None):
    """Fetch crypto news from multiple RSS sources."""
    all_articles = []

    for source in NEWS_SOURCES:
        try:
            if logger:
                logger.info(f"Fetching: {source['name']}...")

            if source["use_proxy"]:
                for proxy in CORS_PROXIES:
                    try:
                        url = proxy + source["rss"]
                        if logger:
                            logger.info(f"Trying proxy: {proxy[:30]}...")

                        response = requests.get(url, timeout=15)
                        response.raise_for_status()

                        articles = parse_feed(response.text, source["name"])
                        if articles:
                            all_articles.extend(articles)
                            if logger:
                                logger.info(
                                    f"Got {len(articles)} articles from {source['name']}"
                                )
                            break
                    except Exception as e:
                        if logger:
                            logger.warning(f"Proxy failed: {e}")
                        continue
            else:
                try:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                    response = requests.get(source["rss"], headers=headers, timeout=15)
                    response.raise_for_status()

                    articles = parse_feed(response.text, source["name"])
                    if articles:
                        all_articles.extend(articles)
                        if logger:
                            logger.info(
                                f"Got {len(articles)} articles from {source['name']} (direct)"
                            )
                except Exception as e:
                    if logger:
                        logger.warning(f"Direct source failed: {e}")
        except Exception as e:
            if logger:
                logger.error(f"Source error {source['name']}: {e}")
            continue

    if logger:
        logger.info(f"Total: {len(all_articles)} raw articles fetched")

    return all_articles
