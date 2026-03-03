#!/bin/bash
# Script d'initialisation du dépôt Git pour crypto-news-bot

echo "🚀 Initialisation du dépôt Git pour crypto-news-bot"
echo "=================================================="
echo ""

# Vérifier si Git est installé
if ! command -v git &> /dev/null; then
    echo "❌ Git n'est pas installé. Installez-le d'abord."
    exit 1
fi

# Vérifier si config.py existe (avec clés sensibles)
if [ -f "config.py" ]; then
    echo "⚠️  ATTENTION : config.py détecté avec vos clés API"
    echo "📋 Vérification du .gitignore..."
    
    if grep -q "config.py" .gitignore; then
        echo "✅ config.py est dans .gitignore"
    else
        echo "❌ ERREUR : config.py n'est PAS dans .gitignore !"
        echo "Ajout de config.py au .gitignore..."
        echo "config.py" >> .gitignore
    fi
fi

# Initialiser le dépôt si ce n'est pas déjà fait
if [ ! -d ".git" ]; then
    echo ""
    echo "📦 Initialisation du dépôt Git..."
    git init
    echo "✅ Dépôt Git initialisé"
else
    echo "✅ Dépôt Git déjà initialisé"
fi

# Vérifier qu'on n'ajoute pas de fichiers sensibles
echo ""
echo "🔍 Vérification des fichiers sensibles..."

SENSITIVE_FILES=("config.py" "posted_articles.txt" "posted_titles.txt" "bot_running.lock" "*.log")
FOUND_SENSITIVE=0

for file in "${SENSITIVE_FILES[@]}"; do
    if git ls-files --error-unmatch "$file" 2>/dev/null; then
        echo "❌ ATTENTION : $file est tracké par Git !"
        FOUND_SENSITIVE=1
    fi
done

if [ $FOUND_SENSITIVE -eq 1 ]; then
    echo ""
    echo "⚠️  Fichiers sensibles détectés dans Git !"
    echo "Voulez-vous les retirer ? (o/n)"
    read -r response
    if [[ "$response" =~ ^([oO][uU][iI]|[oO])$ ]]; then
        for file in "${SENSITIVE_FILES[@]}"; do
            git rm --cached "$file" 2>/dev/null
        done
        echo "✅ Fichiers sensibles retirés du cache Git"
    fi
fi

# Ajouter tous les fichiers (sauf ceux dans .gitignore)
echo ""
echo "📁 Ajout des fichiers au dépôt..."
git add .

# Afficher le statut
echo ""
echo "📊 Statut du dépôt :"
git status

# Vérifier que config.py n'est PAS dans les fichiers à committer
if git diff --cached --name-only | grep -q "config.py"; then
    echo ""
    echo "❌ ERREUR CRITIQUE : config.py est sur le point d'être committé !"
    echo "Annulation..."
    git reset config.py
    exit 1
fi

echo ""
echo "✅ Prêt pour le commit !"
echo ""
echo "Prochaines étapes :"
echo "1. git commit -m 'Initial commit: Crypto News Bot'"
echo "2. Créer un repo sur GitHub : https://github.com/Bulls-Dev"
echo "3. git remote add origin https://github.com/Bulls-Dev/crypto-news-bot.git"
echo "4. git branch -M main"
echo "5. git push -u origin main"
echo ""
echo "⚠️  IMPORTANT : Vérifiez une dernière fois que config.py n'est PAS listé ci-dessus !"
echo ""
