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
        
        # Priority: generated image > RSS image
        image_path = article.get("generated_image")  # FLUX.1 generated image
        image_url = article.get("image_url")  # RSS image fallback

        message = f"""
{emoji} **{translation["titre_fr"]}**

{translation["resume"]}

{translation["description_fr"][:280]}{"..." if len(translation["description_fr"]) > 280 else ""}

[Sources]({article["link"]})
"""

        # Use generated image if available, otherwise RSS image
        if image_path and generate_images:
            try:
                # Send local generated image file
                with open(image_path, 'rb') as photo:
                    await client.send_photo(
                        chat_id=chat_id,
                        photo=photo,
                        caption=message,
                        parse_mode="Markdown",
                    )
                if logger:
                    logger.info(f"✅ Posted with FLUX.1 generated image")
            except Exception as img_error:
                if logger:
                    logger.warning(f"⚠️  Generated image error: {img_error}, trying RSS fallback")
                # Fallback to RSS image
                if image_url:
                    await client.send_photo(
                        chat_id=chat_id,
                        photo=image_url,
                        caption=message,
                        parse_mode="Markdown",
                    )
                else:
                    await client.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode="Markdown",
                        disable_web_page_preview=False,
                    )
        elif image_url and generate_images:
            # Use RSS image if no generated image
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
