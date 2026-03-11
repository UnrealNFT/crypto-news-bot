import random
from telegram.error import TelegramError


async def post_article(
    client,
    article: dict,
    translation: dict,
    chat_id: str,
    emojis: list,
    generate_images: bool,
    logger=None,
):
    """Post translated article to Telegram."""
    try:
        emoji = random.choice(emojis)
        image_url = article.get("image_url")

        message = f"""
{emoji} **{translation["titre_fr"]}**

{translation["resume"]}

{translation["description_fr"][:280]}{"..." if len(translation["description_fr"]) > 280 else ""}

[Sources]({article["link"]})
"""

        if image_url and generate_images:
            try:
                await client.send_photo(
                    chat_id=chat_id,
                    photo=image_url,
                    caption=message,
                    parse_mode="Markdown",
                )
            except Exception as img_error:
                if logger:
                    logger.warning(
                        f"RSS image unavailable: {img_error}, sending without image"
                    )
                await client.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="Markdown",
                    disable_web_page_preview=False,
                )
        else:
            await client.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="Markdown",
                disable_web_page_preview=False,
            )

        if logger:
            logger.info(f"Article posted: {translation['titre_fr'][:50]}...")
        return True

    except TelegramError as e:
        if logger:
            logger.error(f"Telegram error: {e}")
        return False
    except Exception as e:
        if logger:
            logger.error(f"Posting error: {e}")
        return False
