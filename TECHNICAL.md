# 📚 Documentation Technique

## Architecture du Bot

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                     CRYPTO NEWS BOT                          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌─────────┐         ┌─────────┐        ┌─────────┐
   │   RSS   │         │  OpenAI │        │Telegram │
   │  Feeds  │         │   API   │        │   Bot   │
   └─────────┘         └─────────┘        └─────────┘
```

### Composants Principaux

#### 1. RSS Feed Parser (`feedparser`)
```python
# Lecture des flux RSS avec gestion d'erreurs
feed = feedparser.parse(rss_url, agent='Mozilla/5.0...')
```

**UserAgent** :
```python
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```
- Évite les bans IP des serveurs RSS
- Se fait passer pour un navigateur standard
- Contourne les restrictions anti-bot

#### 2. Système de Déduplication

**Méthode 1 : URL tracking**
```python
# Stockage dans posted_articles.txt
if article_url in posted_articles:
    continue  # Article déjà posté
```

**Méthode 2 : Similarité de titres**
```python
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Si similarité > 80%, considéré comme doublon
if similar(new_title, existing_title) > 0.8:
    skip_article()
```

#### 3. Traduction avec ChatGPT

**Prompt utilisé** :
```python
prompt = f"""
Traduis cet article crypto en français de manière professionnelle.
Titre: {title}
Contenu: {description}

Format requis:
- Titre accrocheur (max 100 caractères)
- Résumé concis (2-3 phrases)
- Description complète (3-4 paragraphes)
"""

response = openai_client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}]
)
```

#### 4. Génération d'Images (DALL-E)

**Style configuré** :
```python
IMAGE_STYLE = "Beautiful anime manga cartoon illustration in Studio Ghibli style, with cherry blossoms and warm color palette"

# Génération
image_response = openai_client.images.generate(
    model="dall-e-3",
    prompt=f"{article_title} - {IMAGE_STYLE}",
    size="1024x1024",
    quality="standard",
    n=1
)
```

**Overlay du Logo** :
```python
from PIL import Image

# Ouvre l'image générée
base_image = Image.open("generated.png")

# Ouvre le logo
logo = Image.open("images/logo.png")

# Redimensionne le logo (10% de la largeur)
logo_width = int(base_image.width * 0.1)
logo = logo.resize((logo_width, logo_width))

# Colle le logo en bas à droite
position = (base_image.width - logo_width - 20, 
            base_image.height - logo_width - 20)
base_image.paste(logo, position, logo)

# Sauvegarde
base_image.save("final_image.png")
```

#### 5. Posting sur Telegram

**Format du message** :
```python
message = f"""
{random.choice(CRYPTO_EMOJIS)} **{translated_title}**

📝 {summary}

💎 {full_description}

🔗 {article_url}
📅 {publication_date}
🏷️ {' '.join(HASHTAGS)}

────────────────────
🤖 Traduit par ChatGPT | 📡 Source: {source_name}
"""

# Envoi avec image
await telegram_bot.send_photo(
    chat_id=CHAT_ID,
    photo=open('final_image.png', 'rb'),
    caption=message,
    parse_mode='Markdown'
)
```

## Flux de Traitement

### 1. Collecte des Articles
```python
def fetch_rss_articles():
    articles = []
    for source in NEWS_SOURCES:
        try:
            # Tentative directe
            feed = feedparser.parse(source['rss'])
            
            if feed.bozo:  # Erreur de parsing
                # Utilise un proxy CORS alternatif
                for proxy in CORS_PROXIES:
                    feed = feedparser.parse(proxy + source['rss'])
                    if not feed.bozo:
                        break
            
            for entry in feed.entries[:MAX_ARTICLES_PER_CYCLE]:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.description,
                    'published': entry.published,
                    'source': source['name']
                })
        except Exception as e:
            logger.error(f"Erreur source {source['name']}: {e}")
            continue
    
    return articles
```

### 2. Vérification des Doublons
```python
def is_duplicate(article):
    # Check 1 : URL déjà postée
    if article['link'] in posted_articles:
        return True
    
    # Check 2 : Titre similaire
    for posted_title in posted_titles:
        similarity = SequenceMatcher(
            None, 
            article['title'].lower(), 
            posted_title.lower()
        ).ratio()
        
        if similarity > 0.8:  # 80% de similarité
            return True
    
    return False
```

### 3. Traduction et Formatage
```python
async def translate_article(article):
    system_prompt = """
    Tu es un expert en crypto-monnaies et blockchain.
    Traduis de manière professionnelle en français.
    Utilise un ton informatif mais accessible.
    """
    
    user_prompt = f"""
    Titre: {article['title']}
    Description: {article['description']}
    
    Fournis :
    1. Un titre accrocheur (max 100 caractères)
    2. Un résumé (2-3 phrases)
    3. Une description complète (3-4 paragraphes)
    """
    
    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return parse_gpt_response(response.choices[0].message.content)
```

### 4. Génération et Post
```python
async def process_and_post(article):
    # 1. Vérifier doublon
    if is_duplicate(article):
        logger.info(f"⚠️ Article ignoré (doublon): {article['title']}")
        return
    
    # 2. Traduire
    translation = await translate_article(article)
    
    # 3. Générer image (si activé)
    image_path = None
    if GENERATE_IMAGES:
        image_path = await generate_image(translation['title'])
        image_path = overlay_logo(image_path)
    
    # 4. Formater message
    message = format_telegram_message(
        translation, 
        article, 
        CRYPTO_EMOJIS, 
        HASHTAGS
    )
    
    # 5. Poster sur Telegram
    if image_path:
        await telegram_bot.send_photo(
            chat_id=CHAT_ID,
            photo=open(image_path, 'rb'),
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
    
    # 6. Sauvegarder comme posté
    save_posted_article(article['link'], translation['title'])
    
    logger.info(f"✅ Article posté: {translation['title']}")
```

## Gestion des Erreurs

### Rate Limiting
```python
import time

# Délai entre les posts
await asyncio.sleep(DELAY_BETWEEN_POSTS)

# Gestion des limites Telegram (20 messages/minute)
posts_this_minute = 0
minute_start = time.time()

if posts_this_minute >= 20:
    wait_time = 60 - (time.time() - minute_start)
    if wait_time > 0:
        await asyncio.sleep(wait_time)
    posts_this_minute = 0
    minute_start = time.time()
```

### Retry Logic
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def post_to_telegram(message, photo=None):
    """Retry automatique en cas d'erreur"""
    if photo:
        return await telegram_bot.send_photo(CHAT_ID, photo, message)
    else:
        return await telegram_bot.send_message(CHAT_ID, message)
```

### Proxies CORS Fallback
```python
CORS_PROXIES = [
    "https://api.allorigins.win/raw?url=",
    "https://corsproxy.io/?url=",
    "https://cors-anywhere.herokuapp.com/",
    "https://thingproxy.freeboard.io/fetch/"
]

def fetch_with_fallback(url):
    # Tentative directe
    try:
        return feedparser.parse(url)
    except Exception as e:
        logger.warning(f"Direct fetch failed: {e}")
        
        # Essaie chaque proxy
        for proxy in CORS_PROXIES:
            try:
                return feedparser.parse(proxy + url)
            except:
                continue
        
        raise Exception("All proxies failed")
```

## Scheduling

### Système de Planification
```python
import schedule
import time

def job():
    """Tâche exécutée périodiquement"""
    logger.info(f"🔄 Démarrage du cycle ({datetime.now()})")
    
    articles = fetch_rss_articles()
    logger.info(f"📥 {len(articles)} articles récupérés")
    
    for article in articles:
        try:
            asyncio.run(process_and_post(article))
            time.sleep(DELAY_BETWEEN_POSTS)
        except Exception as e:
            logger.error(f"Erreur: {e}")
            continue

# Planification
schedule.every(POST_INTERVAL_MINUTES).minutes.do(job)

# Boucle principale
while True:
    schedule.run_pending()
    time.sleep(1)
```

### Lock File (Prévention Multi-Instance)
```python
import os
import sys

LOCK_FILE = "bot_running.lock"

def check_if_bot_running():
    if os.path.exists(LOCK_FILE):
        lock_age = time.time() - os.path.getmtime(LOCK_FILE)
        
        if lock_age < 300:  # 5 minutes
            print("❌ Bot déjà en cours d'exécution")
            sys.exit(1)
        else:
            # Fichier lock trop ancien = crash probable
            os.remove(LOCK_FILE)
    
    # Créer le lock file
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

def cleanup():
    """Appelé à l'arrêt du bot"""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    logger.info("🛑 Bot arrêté proprement")

# Enregistrer le cleanup
import atexit
atexit.register(cleanup)
```

## Optimisations

### Cache des Traductions
```python
translation_cache = {}

def get_cached_translation(article_hash):
    if article_hash in translation_cache:
        logger.info("♻️ Utilisation du cache")
        return translation_cache[article_hash]
    return None

def cache_translation(article_hash, translation):
    translation_cache[article_hash] = translation
```

### Compression des Images
```python
from PIL import Image

def optimize_image(image_path):
    img = Image.open(image_path)
    
    # Redimensionner si trop grande
    max_size = (1200, 1200)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Compression JPEG
    img.save(image_path, "JPEG", quality=85, optimize=True)
    
    logger.info(f"📉 Image optimisée: {image_path}")
```

## Métriques et Monitoring

### Logs Structurés
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

# Métriques custom
class MetricsLogger:
    def __init__(self):
        self.articles_fetched = 0
        self.articles_translated = 0
        self.articles_posted = 0
        self.errors = 0
    
    def log_summary(self):
        logger.info("=" * 50)
        logger.info(f"📊 STATISTIQUES")
        logger.info(f"📥 Articles récupérés: {self.articles_fetched}")
        logger.info(f"🤖 Articles traduits: {self.articles_translated}")
        logger.info(f"✅ Articles postés: {self.articles_posted}")
        logger.info(f"❌ Erreurs: {self.errors}")
        logger.info("=" * 50)

metrics = MetricsLogger()
```

## Tests

### Tests Unitaires
```python
# test_bot.py
import unittest
from crypto_news_bot import is_duplicate, similar

class TestBot(unittest.TestCase):
    def test_similarity(self):
        title1 = "Bitcoin reaches new ATH"
        title2 = "Bitcoin reaches new all-time high"
        
        self.assertGreater(similar(title1, title2), 0.7)
    
    def test_duplicate_detection(self):
        article = {'link': 'https://example.com/article1'}
        
        # Simule article déjà posté
        posted_articles.add('https://example.com/article1')
        
        self.assertTrue(is_duplicate(article))

if __name__ == '__main__':
    unittest.main()
```

## Déploiement Production

### Systemd Service (Linux)
```ini
# /etc/systemd/system/cryptobot.service
[Unit]
Description=Crypto News Telegram Bot
After=network.target

[Service]
Type=simple
User=cryptobot
WorkingDirectory=/opt/crypto-bot/tgbot
ExecStart=/usr/bin/python3 crypto_news_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Commandes :
```bash
sudo systemctl enable cryptobot
sudo systemctl start cryptobot
sudo systemctl status cryptobot
```

### Windows Task Scheduler
```powershell
# Créer une tâche planifiée au démarrage
$action = New-ScheduledTaskAction -Execute 'python' -Argument 'C:\crypto-bot\tgbot\crypto_news_bot.py'
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "CryptoBot" -Action $action -Trigger $trigger
```

## Sécurité

### Variables d'Environnement
```python
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
```

### Rate Limiting OpenAI
```python
import openai
from ratelimit import limits, sleep_and_retry

# Max 60 requêtes par minute
@sleep_and_retry
@limits(calls=60, period=60)
def call_openai_api(prompt):
    return openai_client.chat.completions.create(...)
```

---

**Version** : 1.0.0  
**Dernière mise à jour** : Mars 2026