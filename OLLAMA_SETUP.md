# 🦙 Installation Ollama + Llama sur Hetzner

## Modifications apportées au bot

✅ **OpenAI (ChatGPT)** remplacé par **Llama** (gratuit, local)  
✅ **DALL-E** remplacé par **images RSS** (directement depuis les articles)

---

## Installation Ollama sur ton serveur Hetzner

### 1. Installer Ollama

```bash
# Sur ton serveur Hetzner (Ubuntu):
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Télécharger le modèle Llama 3.2

```bash
# Modèle recommandé (léger et performant):
ollama pull llama3.2

# Alternatives selon tes ressources:
# ollama pull mistral      # Plus rapide, bon pour traduction
# ollama pull llama2       # Version stable
```

### 3. Vérifier qu'Ollama tourne

```bash
# Vérifier le service:
systemctl status ollama

# Si pas démarré:
systemctl start ollama
systemctl enable ollama  # Démarre au boot

# Tester l'API:
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Traduis en français: Hello world",
  "stream": false
}'
```

### 4. Déployer le nouveau bot

```bash
# Depuis ton serveur Hetzner:
cd /opt/crypto-bot

# Télécharger la nouvelle version:
mv crypto_news_bot.py crypto_news_bot.py.old.v2
curl -o crypto_news_bot.py https://raw.githubusercontent.com/UnrealNFT/crypto-news-bot/main/crypto_news_bot.py

# Arrêter l'ancien bot:
kill $(ps aux | grep crypto_news_bot.py | grep -v grep | awk '{print $2}')

# Relancer le bot:
cd /opt/crypto-bot && nohup venv/bin/python crypto_news_bot.py > bot.log 2>&1 &

# Surveiller les logs:
tail -f /opt/crypto-bot/bot.log
```

---

## Avantages

✅ **Gratuit** - Plus de quota OpenAI  
✅ **Rapide** - Llama local plus rapide que l'API OpenAI  
✅ **Images réelles** - Photos des articles au lieu de generées  
✅ **Autonome** - Fonctionne hors ligne

---

## Configuration

Dans `config.py`, tu peux contrôler l'affichage des images:

```python
# Afficher les images RSS:
GENERATE_IMAGES = True

# Désactiver les images:
GENERATE_IMAGES = False
```

---

## Résolution de problèmes

### Ollama ne répond pas

```bash
systemctl restart ollama
journalctl -u ollama -f  # Voir les logs
```

### Modèle non trouvé

```bash
ollama list  # Voir les modèles installés
ollama pull llama3.2  # Réinstaller
```

### Bot n'arrive pas à contacter Ollama

```bash
# Vérifier que le port 11434 est accessible:
netstat -tlnp | grep 11434

# Vérifier l'API:
curl http://localhost:11434/api/tags
```

---

## Ressources serveur

**Llama 3.2** (recommandé):
- RAM: ~2 GB
- CPU: 2 cores minimum
- Stockage: ~2 GB

Ton serveur Hetzner **4GB RAM** est parfait! 🎯
