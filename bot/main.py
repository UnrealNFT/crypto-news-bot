import asyncio
import os
import time
import schedule
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import (
    BOT_TOKEN,
    CHAT_ID,
    POST_INTERVAL_MINUTES,
    MAX_ARTICLES_PER_CYCLE,
    DELAY_BETWEEN_POSTS,
    GENERATE_IMAGES,
    LOG_LEVEL,
    CRYPTO_EMOJIS,
)
from src.utils.logger import setup_logger
from src.utils.storage import Storage
from src.rss import fetch_news
from src.deduplication import deduplicate_articles
from src.translation import translate_with_llama
from src.telegram import TelegramClient, post_article


logger = setup_logger(__name__, LOG_LEVEL)
storage = Storage()


def check_if_bot_running():
    """Check if bot is already running."""
    lock_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bot_running.lock"
    )
    try:
        if os.path.exists(lock_file):
            lock_age = time.time() - os.path.getmtime(lock_file)
            if lock_age < 300:
                logger.error("Bot appears to be running already")
                return True
            else:
                os.remove(lock_file)
        return False
    except Exception as e:
        logger.warning(f"Lock check error: {e}")
        return False


def create_lock_file():
    """Create lock file."""
    lock_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bot_running.lock"
    )
    try:
        with open(lock_file, "w") as f:
            f.write(str(os.getpid()))
        logger.info(f"Lock file created (PID: {os.getpid()})")
    except Exception as e:
        logger.warning(f"Lock create error: {e}")


def remove_lock_file():
    """Remove lock file."""
    lock_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bot_running.lock"
    )
    try:
        if os.path.exists(lock_file):
            os.remove(lock_file)
            logger.info("Lock file removed")
    except Exception as e:
        logger.warning(f"Lock remove error: {e}")


async def test_bot(client: TelegramClient):
    """Test bot connection."""
    try:
        me = await client.get_me()
        logger.info(f"Telegram bot connected: @{me.username}")

        await client.send_message(
            chat_id=CHAT_ID,
            text=f"**Bot Crypto News FR** activated!\n\nPosts every {POST_INTERVAL_MINUTES} minutes.",
            parse_mode="Markdown",
        )

        logger.info("Bot test successful!")
        return True
    except Exception as e:
        logger.error(f"Bot test failed: {e}")
        return False


async def process_news(client: TelegramClient):
    """Process news: fetch -> translate -> post."""
    logger.info("Starting news processing...")

    articles = fetch_news(logger)
    if not articles:
        logger.warning("No articles retrieved")
        return

    posted_titles = storage.load_titles()
    unique_articles = deduplicate_articles(
        articles, posted_titles, MAX_ARTICLES_PER_CYCLE
    )
    logger.info(f"{len(unique_articles)} unique articles after deduplication")

    posted_article_ids = storage.load_article_ids()
    new_count = 0

    for article in unique_articles:
        if article["id"] in posted_article_ids:
            continue

        logger.info(f"New article: {article['title'][:50]}...")

        translation = translate_with_llama(article, logger=logger)

        success = await post_article(
            client,
            article,
            translation,
            CHAT_ID,
            CRYPTO_EMOJIS,
            GENERATE_IMAGES,
            logger,
        )

        if success:
            storage.save_article(article["id"], article["title"])
            posted_article_ids.add(article["id"])
            new_count += 1
            await asyncio.sleep(DELAY_BETWEEN_POSTS)

    logger.info(f"Processing complete. {new_count} new articles posted.")


async def run_news_update(client: TelegramClient):
    """Run news update."""
    await process_news(client)


def setup_scheduler(client: TelegramClient):
    """Setup automatic posting schedule."""

    def run_sync():
        asyncio.run(run_news_update(client))

    schedule.every(POST_INTERVAL_MINUTES).minutes.do(run_sync)
    logger.info(f"Scheduler configured: posts every {POST_INTERVAL_MINUTES} minutes")


async def main():
    """Main entry point."""
    logger.info("Starting Crypto News Bot FR...")

    if check_if_bot_running():
        return

    create_lock_file()

    try:
        client = TelegramClient(BOT_TOKEN)

        if not await test_bot(client):
            logger.error("Initial test failed. Check configuration.")
            return

        logger.info("First news processing...")
        await run_news_update(client)

        setup_scheduler(client)

        logger.info("Bot running. Press Ctrl+C to stop.")
        while True:
            schedule.run_pending()
            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("Bot stopped...")
    finally:
        remove_lock_file()


if __name__ == "__main__":
    asyncio.run(main())
