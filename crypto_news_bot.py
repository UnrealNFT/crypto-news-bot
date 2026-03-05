import asyncio
import logging
import feedparser
import requests
from datetime import datetime, timedelta
import schedule
import time
import os
from telegram import Bot
from telegram.error import TelegramError
from openai import OpenAI
import json
import re
import random
from difflib import SequenceMatcher

# Import configuration from config.py
# All sensitive data (API keys) should be in config.py, NOT hardcoded here
from config import *

IMAGE_STYLE = "Beautiful anime manga cartoon illustration in Studio Ghibli style, with cherry blossoms and warm color palette"

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL, logging.INFO)
)
logger = logging.getLogger(__name__)

# Use BOT_TOKEN from config.py
TELEGRAM_BOT_TOKEN = BOT_TOKEN

# Configuration Actualités Crypto
NEWS_SOURCES = [
    {
        "name": "CoinTelegraph",
        "rss": "https://cointelegraph.com/rss",
        "use_proxy": True
    },
    {
        "name": "CoinDesk", 
        "rss": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "use_proxy": True
    },
    {
        "name": "CryptoNews",
        "rss": "https://cryptonews.com/news/feed/",
        "use_proxy": False  # Tentative directe
    }
]

# Proxies CORS alternatifs (en cas de timeout)
CORS_PROXIES = [
    "https://api.allorigins.win/raw?url=",
    "https://corsproxy.io/?url=",
    "https://cors-anywhere.herokuapp.com/",
    "https://thingproxy.freeboard.io/fetch/"
]

# Initialisation des clients
telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Stockage persistant des articles déjà postés ET données de déduplication
# Utilise le répertoire du script pour compatibilité Windows/Linux
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POSTED_ARTICLES_FILE = os.path.join(SCRIPT_DIR, "posted_articles.txt")
POSTED_TITLES_FILE = os.path.join(SCRIPT_DIR, "posted_titles.txt")
LOCK_FILE = os.path.join(SCRIPT_DIR, "bot_running.lock")

def check_if_bot_running():
    """Vérifie si le bot est déjà en cours d'exécution (Windows-safe)"""
    try:
        if os.path.exists(LOCK_FILE):
            # Sur Windows, on vérifie l'âge du fichier (si très récent = probablement actif)
            lock_age = time.time() - os.path.getmtime(LOCK_FILE)
            if lock_age < 300:  # Si le fichier a moins de 5 minutes
                logger.error("❌ Bot semble déjà en cours d'exécution")
                logger.error("❌ Si c'est faux, supprimez: tgbot/bot_running.lock")
                return True
            else:
                # Fichier trop vieux, probablement un crash
                os.remove(LOCK_FILE)
                return False
        return False
    except Exception as e:
        logger.warning(f"⚠️ Erreur vérification lock: {e}")
        return False

def create_lock_file():
    """Crée le fichier de verrouillage"""
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        logger.info(f"🔒 Fichier de verrouillage créé (PID: {os.getpid()})")
    except Exception as e:
        logger.warning(f"⚠️ Erreur création lock: {e}")

def remove_lock_file():
    """Supprime le fichier de verrouillage"""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            logger.info("🔓 Fichier de verrouillage supprimé")
    except Exception as e:
        logger.warning(f"⚠️ Erreur suppression lock: {e}")

def load_posted_articles():
    """Charge l'historique des IDs d'articles postés"""
    try:
        with open(POSTED_ARTICLES_FILE, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def load_posted_titles():
    """Charge l'historique des titres postés depuis le fichier"""
    try:
        with open(POSTED_TITLES_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_posted_article(article_id, title):
    """Sauvegarde un article dans l'historique persistant"""
    try:
        # Sauvegarder l'ID
        with open(POSTED_ARTICLES_FILE, 'a', encoding='utf-8') as f:
            f.write(article_id + '\n')
        # Sauvegarder le titre
        with open(POSTED_TITLES_FILE, 'a', encoding='utf-8') as f:
            f.write(title + '\n')
        # Nettoyage périodique
        cleanup_posted_files()
    except Exception as e:
        logger.warning(f"⚠️ Erreur sauvegarde article: {e}")

def cleanup_posted_files():
    """Nettoie les fichiers d'historique (garde seulement les 200 derniers)"""
    try:
        # Nettoie les IDs
        article_ids = list(load_posted_articles())
        if len(article_ids) > 200:
            article_ids = article_ids[-200:]
            with open(POSTED_ARTICLES_FILE, 'w', encoding='utf-8') as f:
                f.write('\n'.join(article_ids) + '\n')
        
        # Nettoie les titres  
        titles = load_posted_titles()
        if len(titles) > 200:
            titles = titles[-200:]
            with open(POSTED_TITLES_FILE, 'w', encoding='utf-8') as f:
                f.write('\n'.join(titles) + '\n')
    except Exception as e:
        logger.warning(f"⚠️ Erreur nettoyage historique: {e}")

posted_articles = load_posted_articles()  # Charge l'historique des IDs

posted_titles = load_posted_titles()  # Charge l'historique au démarrage

def normalize_title(title):
    """Normalise un titre pour comparaison anti-doublons"""
    if not title:
        return ""
    
    # Minuscules et suppression caractères spéciaux
    normalized = title.lower()
    normalized = re.sub(r'[^a-z0-9\s]', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    # Supprime les mots communs qui polluent
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    words = [w for w in normalized.split() if w not in stop_words and len(w) > 2]
    
    return ' '.join(words)

def calculate_similarity(title1, title2):
    """Calcule la similarité entre 2 titres (0-1)"""
    norm1 = normalize_title(title1)
    norm2 = normalize_title(title2)
    
    if not norm1 or not norm2:
        return 0
    
    # Similarité basée sur SequenceMatcher
    return SequenceMatcher(None, norm1, norm2).ratio()

def is_duplicate_article(article, similarity_threshold=0.75):
    """Vérifie si un article est un doublon d'un article déjà posté"""
    current_title = article['title']
    
    # Vérifie la similarité avec tous les titres déjà postés
    for posted_title in posted_titles:
        similarity = calculate_similarity(current_title, posted_title)
        if similarity >= similarity_threshold:
            logger.info(f"🔄 Doublon détecté: '{current_title[:40]}...' similaire à '{posted_title[:40]}...' ({similarity:.2f})")
            return True
    
    return False

def deduplicate_articles(articles, max_articles=5):
    """Supprime les doublons d'une liste d'articles"""
    unique_articles = []
    seen_titles = []
    
    for article in articles:
        # Skip si c'est un doublon par rapport aux articles de cette session
        is_session_dup = False
        for seen_title in seen_titles:
            if calculate_similarity(article['title'], seen_title) >= 0.80:
                logger.info(f"🔄 Doublon session ignoré: '{article['title'][:40]}...'")
                is_session_dup = True
                break
                
        # Skip si c'est un doublon global
        if not is_session_dup and not is_duplicate_article(article):
            unique_articles.append(article)
            seen_titles.append(article['title'])
            
    # Limite le nombre final d'articles
    return unique_articles[:max_articles]

def get_crypto_news():
    """Récupère les dernières actualités crypto depuis plusieurs sources"""
    all_articles = []
    
    for source in NEWS_SOURCES:
        try:
            logger.info(f"🔍 Source: {source['name']}...")
            
            if source['use_proxy']:
                # Essayer avec les proxies CORS
                for proxy in CORS_PROXIES:
                    try:
                        url = proxy + source['rss']
                        logger.info(f"🔄 Proxy: {proxy[:30]}...")
                        
                        response = requests.get(url, timeout=15)
                        response.raise_for_status()
                        
                        articles = parse_feed(response.text, source['name'])
                        if articles:
                            all_articles.extend(articles)
                            logger.info(f"✅ {len(articles)} articles de {source['name']}")
                            break  # Proxy réussi, pas besoin d'essayer les autres
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Proxy {proxy[:30]}... échoué: {e}")
                        continue
            else:
                # Essai direct (sans proxy)
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(source['rss'], headers=headers, timeout=15)
                    response.raise_for_status()
                    
                    articles = parse_feed(response.text, source['name'])
                    if articles:
                        all_articles.extend(articles)
                        logger.info(f"✅ {len(articles)} articles de {source['name']} (direct)")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Source directe {source['name']} échouée: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Erreur source {source['name']}: {e}")
            continue
    
    # Déduplication intelligente
    logger.info(f"🔍 {len(all_articles)} articles bruts récupérés")
    unique_articles = deduplicate_articles(all_articles, MAX_ARTICLES_PER_CYCLE)
    
    logger.info(f"✅ {len(unique_articles)} articles uniques après déduplication")
    return unique_articles

def parse_feed(xml_content, source_name):
    """Parse un flux RSS et retourne les articles (avec nettoyage avancé)"""
    try:
        feed = feedparser.parse(xml_content)
        
        if not feed.entries:
            return []
        
        articles = []
        for entry in feed.entries[:3]:  # Max 3 par source
            description = getattr(entry, 'description', '')
            description = description if isinstance(description, str) else str(description) if description else ''
            
            # Nettoyage avancé du contenu
            description = clean_content(description)
            title = getattr(entry, 'title', 'Titre non disponible')
            
            # Skip les articles vides ou pourris
            if len(description.strip()) < 20 or "image" in title.lower():
                continue
            
            article = {
                'title': title,
                'description': description,
                'link': getattr(entry, 'link', ''),
                'pub_date': getattr(entry, 'published', ''),
                'id': getattr(entry, 'id', '') or getattr(entry, 'link', ''),
                'source': source_name
            }
            articles.append(article)
            
        return articles
        
    except Exception as e:
        logger.error(f"❌ Erreur parsing feed {source_name}: {e}")
        return []

def clean_content(text):
    """Nettoie le contenu RSS des images et liens parasites"""
    if not text:
        return ""
    
    # Supprime les balises HTML complètement
    text = re.sub(r'<img[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<a[^>]*>.*?</a>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]*>', '', text)
    
    # Supprime les URLs d'images complètes
    text = re.sub(r'https?://[^\s]*\.(jpg|jpeg|png|gif|webp|svg)[^\s]*', '', text, flags=re.IGNORECASE)
    
    # Supprime les références d'images en texte
    text = re.sub(r'\[Image:.*?\]', '', text)
    text = re.sub(r'\(Image:.*?\)', '', text)
    text = re.sub(r'Image\s*:\s*[^\n]*', '', text, flags=re.IGNORECASE)
    
    # Supprime les liens de lecture/navigation
    text = re.sub(r'Read more.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Continue reading.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Source\s*:\s*.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Read full story.*', '', text, flags=re.IGNORECASE)
    
    # Supprime les métadonnées CoinTelegraph
    text = re.sub(r'The post .* appeared first on.*', '', text)
    text = re.sub(r'Originally appeared on.*', '', text)
    
    # Supprime les caractères de formatage et espaces multiples
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', ' ', text)
    
    # Décode les entités HTML
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&apos;', "'")
    text = text.replace('\r', '').replace('\t', ' ')
    
    # Supprime les crochets vides et parenthèses orphelines
    text = re.sub(r'\[\s*\]', '', text)
    text = re.sub(r'\(\s*\)', '', text)
    
    return text.strip()

def translate_with_chatgpt(article, max_retries=3):
    """Traduit un article en français avec ChatGPT (avec retry)"""
    
    for attempt in range(max_retries):
        try:
            prompt = f"""
Traduis cet article crypto en français de manière professionnelle et engaging. 
Garde le même style journalistique et les termes techniques appropriés.

Titre: {article['title']}
Description: {article['description'][:500]}...

Réponds au format JSON:
{{
    "titre_fr": "titre traduit",
    "description_fr": "description traduite",
    "resume": "résumé en 2-3 phrases"
}}
"""

            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Tu es un expert traducteur crypto français. Tu traduis les actualités blockchain de manière claire et professionnelle."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7,
            )
            
            # Vérification de sécurité pour éviter les erreurs de type
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Réponse OpenAI vide")
                
            # Nettoie la réponse JSON si nécessaire
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
                
            result = json.loads(content)
            
            # Validation des champs requis
            if not all(key in result for key in ['titre_fr', 'description_fr', 'resume']):
                raise ValueError("Champs JSON manquants")
                
            logger.info(f"✅ Traduction réussie: {article['title'][:50]}...")
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Erreur JSON attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Pause avant retry
        except Exception as e:
            logger.warning(f"⚠️ Erreur traduction attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
    
    # Traduction de secours après échec
    logger.error(f"❌ Échec traduction après {max_retries} tentatives pour: {article['title'][:50]}...")
    return {
        "titre_fr": article['title'],
        "description_fr": article['description'][:300] if article['description'] else "Nouvel article crypto disponible.",
        "resume": "📰 Article crypto important à consulter."
    }

async def generate_image_with_dalle(article_title):
    """Génère une image avec DALL-E pour illustrer l'article (style manga/anime tech)"""
    try:
        # EXTRACTION ET NETTOYAGE DES MOTS-CLÉS (SANS DÉCLENCHEURS BITCOIN)
        title_lower = article_title.lower()
        
        # Mots-clés SAFE qui ne déclenchent pas les logos Bitcoin
        key_words = []
        safe_words = ['ethereum', 'smart', 'accounts', 'technology', 'development', 'network', 'protocol',
                     'trading', 'market', 'legal', 'court', 'regulation', 'partnership', 'adoption',
                     'finance', 'digital', 'innovation', 'security', 'platform', 'system']
        
        # BANNIR les mots qui déclenchent Bitcoin automatiquement
        banned_words = ['bitcoin', 'btc', 'crypto', 'cryptocurrency', 'token', 'coin', 'mining', 'wallet', 'blockchain']
        
        for word in safe_words:
            if word in title_lower:
                # Remplacer par des équivalents safe
                if word == 'token':
                    key_words.append('digital asset')
                elif word == 'crypto':
                    key_words.append('fintech')
                else:
                    key_words.append(word)
        
        # Si article sur Bitcoin, utiliser "digital finance" à la place
        if any(banned in title_lower for banned in banned_words):
            key_words = ['digital finance', 'technology', 'innovation']
        
        # Limiter à 3 mots max
        key_words = key_words[:3]
        keywords_str = ', '.join(key_words) if key_words else 'digital technology'
        
        # PROMPT MANGA CARTOON COLORÉ (FINI LE CYBERPUNK!)
        prompt = f"""Beautiful anime manga cartoon illustration for: {keywords_str}.
Bright colorful manga style with vibrant colors and clean cartoon aesthetic.
Cheerful and optimistic anime environment with soft lighting and pleasant atmosphere.
Beautiful nature elements like cherry blossoms, clear skies, or peaceful Japanese landscapes.
Warm color palette with bright blues, soft pinks, gentle greens, and golden yellows.
Clean cartoon style like Studio Ghibli or modern anime backgrounds.
NO logos, NO symbols, NO cryptocurrency branding, NO dark or tech elements.
Pure beautiful manga cartoon scenery representing: {article_title[:40]}
Completely clear top-left corner for logo overlay.
High-quality anime cartoon art, cheerful and welcoming atmosphere."""
        
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Vérification de sécurité pour éviter les erreurs de type
        if response and response.data and len(response.data) > 0:
            image_url = response.data[0].url
            
            # Ajouter le logo et utiliser l'image locale si possible
            final_image = await add_logo_to_image(image_url)
            
            logger.info(f"✅ Image manga générée: {article_title[:30]}...")
            return final_image  # Retourne soit le chemin local, soit l'URL originale
        else:
            logger.warning("⚠️ Réponse DALL-E vide ou invalide")
            return None
        
    except Exception as e:
        logger.error(f"❌ Erreur génération image DALL-E: {e}")
        return None

async def add_logo_to_image(image_url):
    """Ajoute le logo logoFR.png en haut à droite de l'image"""
    try:
        from PIL import Image
        import requests
        from io import BytesIO
        import os
        
        # Télécharge l'image DALL-E
        logger.info(f"📋 Téléchargement image: {image_url[:50]}...")
        response = requests.get(image_url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        logger.info(f"🖼️ Image chargée: {img.size} mode: {img.mode}")
        
        # Vérifie si le logo existe (chemin absolu pour serveur)
        logo_path = os.path.join(SCRIPT_DIR, "Logofr.PNG")
        logger.info(f"🔍 Recherche logo: {logo_path}")
        
        if os.path.exists(logo_path):
            logger.info("✅ Logo trouvé ! Application en cours...")
            # Charge le logo
            logo = Image.open(logo_path)
            
            # Redimensionne le logo (taille fixe 200x200 légèrement plus gros)
            logo_target_size = 200
            logo = logo.resize((logo_target_size, logo_target_size), Image.Resampling.LANCZOS)
            
            # Position en haut À GAUCHE (marge de 15px)
            x_pos = 15
            y_pos = 15
            
            logger.info(f"📏 Logo redimensionné: {logo_target_size}x{logo_target_size} à position GAUCHE ({x_pos}, {y_pos})")
            
            # FORCE la transparence si le logo a un canal alpha
            if logo.mode in ('RGBA', 'LA') or (logo.mode == 'P' and 'transparency' in logo.info):
                # Convertit en RGBA si nécessaire
                if logo.mode != 'RGBA':
                    logo = logo.convert('RGBA')
                    
                # Applique le logo avec transparence
                img.paste(logo, (x_pos, y_pos), logo)
                logger.info("✅ Logo appliqué EN HAUT À GAUCHE avec transparence !")
            else:
                # Logo sans transparence, convertit l'image background en blanc
                if logo.mode != 'RGB':
                    logo = logo.convert('RGB')
                img.paste(logo, (x_pos, y_pos))
                logger.info("✅ Logo appliqué EN HAUT À GAUCHE sans transparence !")
            
            # Sauvegarde l'image avec logo (chemin absolu pour serveur)
            output_path = os.path.join(SCRIPT_DIR, f"temp_image_{int(time.time())}.png")
            img.save(output_path)
            
            logger.info("✅ Logo superposé sur l'image !")
            # Retourne le chemin local pour envoi direct à Telegram
            return output_path
        else:
            logger.warning("⚠️ Logo Logofr.PNG introuvable, image sans logo")
            return image_url
            
    except Exception as e:
        logger.error(f"❌ Erreur ajout logo: {e}")
        return image_url  # Retourne l'image originale en cas d'erreur

async def upload_temp_image(image_path):
    """Upload temporaire d'une image (pour l'instant retourne None)"""
    # TODO: Implémenter upload vers service d'hébergement temporaire
    # Pour l'instant, on garde l'image DALL-E originale
    return None

async def post_to_telegram(article, translation):
    """Poste l'article traduit sur Telegram avec image générée style manga"""
    try:
        # Sélection d'emojis aléatoires
        emoji = random.choice(CRYPTO_EMOJIS)
        
        # Génération d'image (optionnel)
        image_url = None
        if GENERATE_IMAGES:  # Option configurable
            image_url = await generate_image_with_dalle(translation['titre_fr'])
        
        # Format du message épuré (sans hashtags)
        message = f"""
{emoji} **{translation['titre_fr']}**

📝 {translation['resume']}

💵 {translation['description_fr'][:280]}{'...' if len(translation['description_fr']) > 280 else ''}

🔗 [Sources]({article['link']})
"""
        
        # Envoi avec image locale (avec logo) ou URL
        if image_url:
            if isinstance(image_url, str) and image_url.startswith('tgbot/'):
                # Image locale avec logo
                with open(image_url, 'rb') as photo:
                    await telegram_bot.send_photo(
                        chat_id=CHAT_ID,
                        photo=photo,
                        caption=message,
                        parse_mode='Markdown'
                    )
                # Supprime le fichier temporaire
                import os
                os.remove(image_url)
            else:
                # Image URL DALL-E originale
                await telegram_bot.send_photo(
                    chat_id=CHAT_ID,
                    photo=image_url,
                    caption=message,
                    parse_mode='Markdown'
                )
        else:
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
        
        logger.info(f"✅ Article posté sur Telegram: {translation['titre_fr'][:50]}...")
        return True
        
    except TelegramError as e:
        logger.error(f"❌ Erreur Telegram: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur posting: {e}")
        return False

async def process_news():
    """Traite les actualités: récupération -> traduction -> posting"""
    logger.info("🔄 Début du traitement des actualités...")
    
    # Récupération des actualités
    articles = get_crypto_news()
    if not articles:
        logger.warning("⚠️ Aucun article récupéré")
        return
    
    new_articles_count = 0
    
    for article in articles:
        # Vérifier si l'article a déjà été posté
        if article['id'] in posted_articles:
            continue
            
        logger.info(f"🆕 Nouvel article: {article['title'][:50]}...")
        
        # Traduction avec ChatGPT
        translation = translate_with_chatgpt(article)
        
        # Posting sur Telegram
        success = await post_to_telegram(article, translation)
        
        if success:
            # Sauvegarder dans l'historique persistant (ID + titre)
            save_posted_article(article['id'], article['title'])
            posted_articles.add(article['id'])  # Aussi en mémoire pour cette session
            new_articles_count += 1
            
            # Délai entre les posts pour éviter le spam
            await asyncio.sleep(DELAY_BETWEEN_POSTS)
    
    logger.info(f"✅ Traitement terminé. {new_articles_count} nouveaux articles postés.")

def run_news_update():
    """Lance la mise à jour des actualités (version sync)"""
    asyncio.run(process_news())

# Configuration du planning automatique
def setup_scheduler():
    """Configure le planning de posting automatique"""
    # Poste selon l'intervalle configuré
    schedule.every(POST_INTERVAL_MINUTES).minutes.do(run_news_update)
    
    logger.info(f"📅 Scheduler configuré: posts toutes les {POST_INTERVAL_MINUTES} minutes")

async def test_bot():
    """Test de fonctionnement du bot"""
    try:
        # Test connexion Telegram
        me = await telegram_bot.get_me()
        logger.info(f"🤖 Bot Telegram connecté: @{me.username}")
        
        # Test message
        await telegram_bot.send_message(
            chat_id=CHAT_ID,
            text=f"🚀 **Bot Crypto News FR** activé!\n\n📰 Je vais poster les actualités CoinTelegraph traduites en français.\n\n⚡ Actualisation: toutes les {POST_INTERVAL_MINUTES} minutes",
            parse_mode='Markdown'
        )
        
        logger.info("✅ Test bot réussi!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test bot: {e}")
        return False

def main():
    """Fonction principale"""
    logger.info("🚀 Démarrage du Bot Crypto News FR...")
    
    # Vérification si le bot est déjà en cours d'exécution
    if check_if_bot_running():
        return  # Sortir si une instance est déjà active
    
    # Créer le fichier de verrouillage
    create_lock_file()
    
    try:
        # Test initial
        if not asyncio.run(test_bot()):
            logger.error("❌ Échec du test initial. Vérifiez votre configuration.")
            return
        
        # Premier run immédiat
        logger.info("🔄 Premier traitement des actualités...")
        run_news_update()
        
        # Configuration du scheduler
        setup_scheduler()
        
        # Boucle principale
        logger.info("⏰ Bot en fonctionnement. Ctrl+C pour arrêter.")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérification toutes les minutes
            
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt du bot...")
    finally:
        # Toujours supprimer le fichier de verrouillage
        remove_lock_file()

if __name__ == "__main__":
    main()