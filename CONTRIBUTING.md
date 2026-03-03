# 🤝 Guide de Contribution

Merci de votre intérêt pour contribuer au Bot Crypto News FR ! Ce guide vous aidera à démarrer.

## 🚀 Comment Contribuer

### 1. Fork & Clone
```bash
# Fork le repo sur GitHub, puis :
git clone https://github.com/votre-username/crypto-news-bot.git
cd crypto-news-bot
```

### 2. Configuration de l'Environnement
```bash
# Créer un environnement virtuel
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Activer (Linux/Mac)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Copier la config
cp config.py.example config.py
# Éditer config.py avec vos clés de test
```

### 3. Créer une Branche
```bash
git checkout -b feature/nom-de-votre-feature
# ou
git checkout -b fix/correction-du-bug
```

### 4. Développer
```python
# Suivre les conventions de code Python (PEP 8)
# Ajouter des docstrings à vos fonctions

def ma_nouvelle_fonction(param):
    """
    Description claire de ce que fait la fonction.
    
    Args:
        param (str): Description du paramètre
        
    Returns:
        dict: Description du retour
    """
    pass
```

### 5. Tester
```bash
# Exécuter les tests
python -m pytest tests/

# Vérifier le style de code
flake8 crypto_news_bot.py

# Tester manuellement
python crypto_news_bot.py
```

### 6. Commit
```bash
# Conventions de commit :
git commit -m "feat: ajout d'une nouvelle source RSS"
git commit -m "fix: correction du parsing des dates"
git commit -m "docs: mise à jour du README"
git commit -m "refactor: optimisation de la déduplication"
```

**Préfixes de commit** :
- `feat:` - Nouvelle fonctionnalité
- `fix:` - Correction de bug
- `docs:` - Documentation
- `style:` - Formatage, point-virgules manquants, etc.
- `refactor:` - Refactoring du code
- `test:` - Ajout de tests
- `chore:` - Mise à jour des tâches de maintenance

### 7. Push & Pull Request
```bash
git push origin feature/nom-de-votre-feature
```

Puis créez une Pull Request sur GitHub avec :
- **Titre clair** : "Ajout du support de Decrypt.co"
- **Description** : Expliquez ce que fait votre PR
- **Tests** : Mentionnez comment vous avez testé
- **Screenshots** : Si applicable

## 📋 Checklist PR

Avant de soumettre votre Pull Request :

- [ ] Le code respecte PEP 8
- [ ] J'ai ajouté des docstrings
- [ ] J'ai testé localement
- [ ] Les tests passent
- [ ] J'ai mis à jour la documentation si nécessaire
- [ ] Pas de clés API dans le code
- [ ] Les commits sont clairs et descriptifs

## 🎯 Domaines de Contribution

### Nouvelles Sources RSS
```python
# Dans config.py
NEWS_SOURCES = [
    {
        "name": "NomDuSite",
        "rss": "https://example.com/rss",
        "use_proxy": False
    }
]
```

### Améliorations de Traduction
- Améliorer les prompts ChatGPT
- Ajouter des glossaires crypto
- Supporter d'autres langues

### Génération d'Images
- Nouveaux styles DALL-E
- Optimisations de compression
- Templates de design

### Features
- Système de vote sur les articles
- Statistiques avancées
- Dashboard web de monitoring
- Support multi-canaux
- Filtrage par catégorie (DeFi, NFT, etc.)

### Optimisations
- Cache Redis pour les traductions
- Base de données SQLite pour historique
- API REST pour contrôle à distance
- Webhooks pour notifications

## 🐛 Signaler un Bug

Si vous trouvez un bug, créez une [Issue](https://github.com/Bulls-Dev/crypto-news-bot/issues) avec :

**Template** :
```markdown
**Description du bug**
Une description claire du problème.

**Reproduire le bug**
1. Lancer le bot avec '...'
2. Attendre 5 minutes
3. Voir l'erreur

**Comportement attendu**
Ce qui devrait se passer.

**Logs**
```
[Coller les logs d'erreur ici]
```

**Environnement**
- OS: Windows 11 / Ubuntu 22.04
- Python: 3.11.0
- Version du bot: 1.0.0
```

## 💡 Proposer une Feature

Créez une [Issue](https://github.com/Bulls-Dev/crypto-news-bot/issues) avec :

**Template** :
```markdown
**Feature Request**
Description claire de la fonctionnalité.

**Cas d'utilisation**
Pourquoi cette feature serait utile ?

**Solution proposée**
Comment l'implémenter (si vous avez une idée).

**Alternatives**
Autres approches possibles.
```

## 🎨 Standards de Code

### Style Python
```python
# Bon ✅
def fetch_articles(source_name: str, max_count: int = 5) -> list:
    """
    Récupère les articles d'une source RSS.
    
    Args:
        source_name: Nom de la source RSS
        max_count: Nombre maximum d'articles
        
    Returns:
        Liste des articles récupérés
    """
    articles = []
    # ... code
    return articles

# Mauvais ❌
def get_stuff(x):
    l = []
    # ... code sans explication
    return l
```

### Gestion d'Erreurs
```python
# Bon ✅
try:
    feed = feedparser.parse(rss_url)
    logger.info(f"✅ Feed récupéré: {source_name}")
except Exception as e:
    logger.error(f"❌ Erreur RSS {source_name}: {e}")
    return []

# Mauvais ❌
try:
    feed = feedparser.parse(rss_url)
except:
    pass  # Erreur silencieuse
```

### Logging
```python
# Bon ✅
logger.info(f"📥 {len(articles)} articles récupérés")
logger.warning(f"⚠️ Timeout sur {source_name}, retry...")
logger.error(f"❌ Erreur critique: {error_message}")

# Mauvais ❌
print("got articles")  # Pas de contexte
```

## 🧪 Tests

### Écrire des Tests
```python
# tests/test_deduplication.py
import unittest
from crypto_news_bot import is_duplicate, similar

class TestDeduplication(unittest.TestCase):
    def test_exact_duplicate(self):
        """Test détection doublon exact"""
        article = {'link': 'https://test.com/article1'}
        posted_articles.add('https://test.com/article1')
        
        self.assertTrue(is_duplicate(article))
    
    def test_similar_titles(self):
        """Test détection titres similaires"""
        title1 = "Bitcoin reaches $100k"
        title2 = "Bitcoin reaches 100000 USD"
        
        similarity = similar(title1, title2)
        self.assertGreater(similarity, 0.7)

if __name__ == '__main__':
    unittest.main()
```

### Lancer les Tests
```bash
# Tous les tests
python -m pytest tests/ -v

# Test spécifique
python -m pytest tests/test_deduplication.py -v

# Avec couverture
python -m pytest tests/ --cov=crypto_news_bot
```

## 📝 Documentation

### Docstrings
Utilisez le format Google :
```python
def translate_article(article: dict, target_lang: str = "fr") -> dict:
    """
    Traduit un article dans la langue cible.
    
    Args:
        article (dict): Article à traduire avec keys 'title', 'description'
        target_lang (str): Code langue cible (défaut: 'fr')
        
    Returns:
        dict: Article traduit avec keys 'title', 'summary', 'description'
        
    Raises:
        OpenAIError: Si l'API OpenAI échoue
        ValueError: Si l'article est invalide
        
    Example:
        >>> article = {'title': 'Bitcoin hits ATH', 'description': '...'}
        >>> translated = translate_article(article)
        >>> print(translated['title'])
        'Bitcoin atteint un nouveau sommet'
    """
    pass
```

### Commentaires
```python
# Bon ✅ - Explique le POURQUOI
# On utilise un proxy CORS car certains sites bloquent les requêtes directes
feed = feedparser.parse(CORS_PROXY + rss_url)

# Mauvais ❌ - Explique le QUOI (évident dans le code)
# Parse le feed RSS
feed = feedparser.parse(rss_url)
```

## 🏗️ Architecture

Si vous ajoutez une fonctionnalité majeure, documentez l'architecture :

```python
"""
Module: advanced_deduplication.py

Architecture:
┌─────────────────────┐
│  Article Parser     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Hash Generator     │ ← Génère empreinte unique
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Database Query     │ ← Vérifie dans la DB
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Similarity Check   │ ← ML-based comparison
└─────────────────────┘

Notes:
- Utilise SHA-256 pour le hashing
- Base de données SQLite pour persistance
- Modèle ML: sentence-transformers
"""
```

## 🤝 Code Review

Votre PR sera review selon :

✅ **Critères d'acceptation** :
- Code fonctionnel et testé
- Respecte les standards
- Documentation à jour
- Pas d'impact négatif sur l'existant
- Commits atomiques et clairs

❌ **Raisons de refus** :
- Code non testé
- Break les fonctionnalités existantes
- Clés API hardcodées
- Pas de documentation
- Style de code inconsistant

## 📞 Contact

Des questions ? Rejoignez la discussion :

- **Telegram** : [@crypto_francophone](https://t.me/crypto_francophone)
- **Issues** : [GitHub Issues](https://github.com/Bulls-Dev/crypto-news-bot/issues)
- **Email** : crypto-bot@example.com

## 📜 License

En contribuant, vous acceptez que vos contributions soient sous [MIT License](LICENSE).

---

🙏 **Merci pour votre contribution !** 🚀