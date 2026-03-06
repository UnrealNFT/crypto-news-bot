import json
import time
import requests


def translate_with_llama(article: dict, max_retries: int = 3, logger=None) -> dict:
    """Translate article to French using Llama via Ollama."""

    for attempt in range(max_retries):
        try:
            prompt = f"""Traduis cet article crypto en français. Réponds UNIQUEMENT avec du JSON valide, sans texte explicatif.

Titre: {article["title"]}
Description: {article["description"][:500]}

FORMAT DE RÉPONSE (copie exactement ce format):
{{
    "titre_fr": "ton titre traduit ici",
    "description_fr": "ta description traduite ici",
    "resume": "ton résumé en 2-3 phrases ici"
}}

Réponds maintenant avec SEULEMENT le JSON:"""

            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3:latest",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7},
                },
                timeout=120,
            )

            if response.status_code != 200:
                raise ValueError(f"Ollama API error: {response.status_code}")

            content = response.json().get("response", "")

            if attempt == 0 and logger:
                logger.info(
                    f"Llama response ({len(content)} chars): {content[:200]}..."
                )

            content = content.strip()

            import re

            json_match = re.search(
                r'\{[^{}]*"titre_fr"[^{}]*"description_fr"[^{}]*"resume"[^{}]*\}',
                content,
                re.DOTALL,
            )
            if json_match:
                content = json_match.group(0)
            else:
                if content.startswith("```json"):
                    content = content[7:]
                elif content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

            if not content:
                raise ValueError("Empty response from Llama")

            result = json.loads(content)

            if not all(
                key in result for key in ["titre_fr", "description_fr", "resume"]
            ):
                raise ValueError("Missing JSON fields")

            if logger:
                logger.info(f"Translation success: {article['title'][:50]}...")
            return result

        except json.JSONDecodeError as e:
            if logger:
                logger.warning(f"JSON error attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
        except Exception as e:
            if logger:
                logger.warning(
                    f"Translation error attempt {attempt + 1}/{max_retries}: {e}"
                )
            if attempt < max_retries - 1:
                time.sleep(1)

    if logger:
        logger.error(
            f"Translation failed after {max_retries} attempts: {article['title'][:50]}..."
        )
    return {
        "titre_fr": article["title"],
        "description_fr": article["description"][:300]
        if article["description"]
        else "Nouvel article crypto disponible.",
        "resume": "Article crypto important a consulter.",
    }
