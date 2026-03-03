@echo off
REM Script d'initialisation du dépôt Git pour crypto-news-bot (Windows)

echo ================================================
echo 🚀 Initialisation du dépôt Git pour crypto-news-bot
echo ================================================
echo.

REM Vérifier si Git est installé
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git n'est pas installé. Téléchargez-le sur git-scm.com
    pause
    exit /b 1
)

REM Vérifier si config.py existe (avec clés sensibles)
if exist "config.py" (
    echo ⚠️  ATTENTION : config.py détecté avec vos clés API
    echo 📋 Vérification du .gitignore...
    
    findstr /C:"config.py" .gitignore >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo ✅ config.py est dans .gitignore
    ) else (
        echo ❌ ERREUR : config.py n'est PAS dans .gitignore !
        echo Ajout de config.py au .gitignore...
        echo config.py >> .gitignore
    )
)

REM Initialiser le dépôt si ce n'est pas déjà fait
if not exist ".git" (
    echo.
    echo 📦 Initialisation du dépôt Git...
    git init
    echo ✅ Dépôt Git initialisé
) else (
    echo ✅ Dépôt Git déjà initialisé
)

REM Vérifier qu'on n'ajoute pas de fichiers sensibles
echo.
echo 🔍 Vérification des fichiers sensibles...

git ls-files config.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ❌ ATTENTION : config.py est tracké par Git !
    echo Voulez-vous le retirer ? (O/N)
    set /p response=
    if /i "%response%"=="O" (
        git rm --cached config.py
        echo ✅ config.py retiré du cache Git
    )
)

REM Ajouter tous les fichiers (sauf ceux dans .gitignore)
echo.
echo 📁 Ajout des fichiers au dépôt...
git add .

REM Afficher le statut
echo.
echo 📊 Statut du dépôt :
git status

REM Vérifier que config.py n'est PAS dans les fichiers à committer
git diff --cached --name-only | findstr /C:"config.py" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ❌ ERREUR CRITIQUE : config.py est sur le point d'être committé !
    echo Annulation...
    git reset config.py
    pause
    exit /b 1
)

echo.
echo ✅ Prêt pour le commit !
echo.
echo Prochaines étapes :
echo 1. git commit -m "Initial commit: Crypto News Bot"
echo 2. Créer un repo sur GitHub : https://github.com/Bulls-Dev
echo 3. git remote add origin https://github.com/Bulls-Dev/crypto-news-bot.git
echo 4. git branch -M main
echo 5. git push -u origin main
echo.
echo ⚠️  IMPORTANT : Vérifiez une dernière fois que config.py n'est PAS listé ci-dessus !
echo.
pause
