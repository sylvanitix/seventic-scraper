#!/bin/bash
# Script pour installer Chrome/Chromium sur Render.com

echo "🔧 Installation de Chrome pour Selenium..."

# Détecte le système
if [ -f /etc/debian_version ]; then
    echo "📦 Système Debian/Ubuntu détecté"

    # Met à jour les packages
    apt-get update

    # Installe Chromium et les dépendances
    apt-get install -y \
        chromium-browser \
        chromium-chromedriver \
        xvfb \
        x11-utils \
        wget \
        gnupg2

    # Vérifie l'installation
    if command -v chromium-browser &> /dev/null; then
        echo "✅ Chromium installé avec succès"
        chromium-browser --version
    else
        echo "❌ Échec de l'installation de Chromium"
        exit 1
    fi
else
    echo "⚠️  Système non reconnu - installation ignorée"
fi

echo "✅ Installation terminée"
