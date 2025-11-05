# Web Scraper Avancé

Un outil de scraping puissant et flexible pour extraire des données de sites web, y compris ceux utilisant du contenu chargé dynamiquement en JavaScript.

## Caractéristiques

### Scraping
- **Selenium WebDriver** : Support complet pour les sites JavaScript/React/Vue
- **Gestion des iframes** : Extraction automatique du contenu dans les iframes
- **Rotation de User-Agent** : Évite les blocages
- **Support Proxy** : Configuration optionnelle de proxy
- **Rate Limiting** : Délais configurables entre les requêtes
- **Retry Logic** : Réessai automatique en cas d'échec
- **Scroll Automatique** : Charge le contenu avec défilement infini
- **Mode Headless** : Exécution avec ou sans interface graphique

### Recherche de Domaines
- **Clearbit API gratuite** : Autocomplete + Logo API
- **Validation stricte** : Anti-domaines parkés et faux positifs
- **Score de confiance** : 0-100% avec labels (Très élevée/Élevée/Moyenne)
- **Taux de faux positifs** : Estimation 5-40% selon confiance
- **Tri par fiabilité** : Résultats ordonnés par score

### Enrichissement de Données
- **Scraping web intelligent** : Contact pages, mentions légales
- **Pappers.fr API** : 10,000/mois gratuit (infos légales + dirigeants FR)
- **Hunter.io API** : 50/mois gratuit (emails professionnels)
- **LinkedIn detection** : URLs entreprises et profils
- **Multi-niveaux** : Combine plusieurs sources pour maximiser qualité

### Export
- **Formats multiples** : JSON, CSV, Excel
- **Logging complet** : Logs détaillés avec couleurs
- **Statistiques** : Analyse de qualité des résultats

## Installation

### Prérequis

- Python 3.8+
- Chrome/Chromium installé

### Étapes

1. Cloner ou télécharger le projet

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer l'environnement :
```bash
cp .env.example .env
```

Éditer `.env` selon vos besoins.

## Configuration

Éditez le fichier `.env` :

```env
# Mode sans tête (True = pas d'interface visible)
HEADLESS_MODE=True

# Timeouts
PAGE_LOAD_TIMEOUT=30
IMPLICIT_WAIT=10

# Délais entre requêtes (secondes)
REQUEST_DELAY=2.0

# Nombre de tentatives en cas d'erreur
MAX_RETRIES=3
RETRY_DELAY=5

# Proxy (optionnel)
USE_PROXY=False
PROXY_HOST=
PROXY_PORT=

# Format d'export (json, csv, excel, all)
EXPORT_FORMAT=all

# Dossier de sortie
OUTPUT_DIR=output
```

## Utilisation

### Pipeline Complet Equipauto

#### 1. Scraper les exposants
```bash
python equipauto_scraper_fast.py
```
Extrait 2514 exposants en ~25 secondes.

#### 2. Nettoyer les données
```bash
python clean_data.py
```
Déduplique vers 1301 entreprises uniques.

#### 3. Trouver les domaines
```bash
python domain_finder.py
```
Trouve les sites web avec score de confiance (0-100%) et taux de faux positifs estimé.

#### 4. Enrichir les données
```bash
python company_enricher.py
```
Extrait emails, téléphones, LinkedIn entreprise, et infos dirigeants.

**Résultats** : JSON, CSV et Excel dans `output/`

#### Interprétation des scores de confiance

| Score | Label | Faux Positif | Action Recommandée |
|-------|-------|--------------|-------------------|
| ≥90% | Très élevée | ~5% | Accepter avec confiance |
| 70-90% | Élevée | ~15% | Vérifier rapidement |
| 50-70% | Moyenne | ~40% | ⚠️ VALIDATION MANUELLE OBLIGATOIRE |

**Important** : Toujours valider manuellement les domaines avec confiance < 90%. Voir `DOMAIN_FINDER_GUIDE.md` pour le workflow détaillé.

### Scraper Générique

Pour créer votre propre scraper :

```python
from scraper import WebScraper

# Définir les sélecteurs CSS
selectors = {
    'container': '.item-class',  # Sélecteur du conteneur
    'title': 'h2.title',
    'price': '.price',
    'description': '.description',
    'link': 'a.item-link',
    'next_button': '.pagination-next'
}

# Initialiser le scraper
scraper = WebScraper(headless=True)

try:
    # Scraper l'URL
    url = 'https://example.com/listings'
    data = scraper.scrape_url(url, selectors, max_pages=10)

    # Exporter les données
    scraper.export_data(format='all', filename='my_data')

finally:
    scraper.close()
```

## Structure du Projet

```
web-scraper/
├── config.py                    # Configuration centralisée
├── scraper.py                   # Scraper générique réutilisable
├── equipauto_scraper_fast.py    # Scraper optimisé Equipauto
├── clean_data.py                # Nettoyage et déduplication
├── domain_finder.py             # Recherche de domaines avec scoring
├── company_enricher.py          # Enrichissement données entreprises
├── requirements.txt             # Dépendances Python
├── .env.example                 # Exemple de configuration
├── .env                         # Configuration locale (à créer)
├── README.md                    # Documentation principale
├── README_*.md                  # Documentation par outil
├── DOMAIN_FINDER_GUIDE.md       # Guide complet domain finder
├── API_SETUP_GUIDE.md           # Guide configuration APIs gratuites
├── output/                      # Dossier de sortie (auto-créé)
└── scraper.log                  # Fichier de logs
```

## Personnalisation

### Trouver les bons sélecteurs CSS

1. Ouvrir le site dans Chrome
2. Appuyer sur F12 pour ouvrir DevTools
3. Utiliser l'outil d'inspection (Ctrl+Shift+C)
4. Cliquer sur les éléments à extraire
5. Noter les classes et identifiants

### Gérer la pagination

Le scraper gère automatiquement la pagination si vous fournissez le sélecteur `next_button` :

```python
selectors = {
    # ... autres sélecteurs
    'next_button': '.next-page, .pagination-next, [aria-label="Next"]'
}
```

### Gérer les iframes

Le scraper détecte et gère automatiquement les iframes. Pour forcer un comportement spécifique :

```python
scraper = WebScraper()
scraper.setup_driver()
scraper.driver.get(url)
scraper.handle_iframes()  # Bascule vers l'iframe
```

### Ajouter des délais personnalisés

```python
import time

scraper = WebScraper()
scraper.setup_driver()
scraper.driver.get(url)

# Attendre un élément spécifique
scraper.wait_for_element(By.CSS_SELECTOR, '.content', timeout=20)

# Délai fixe
time.sleep(3)

# Scroll avec délai
scraper.scroll_to_bottom(pause_time=2)
```

## Bonnes Pratiques

1. **Respecter les robots.txt** : Vérifiez toujours `/robots.txt` du site
2. **Rate limiting** : Ne pas surcharger les serveurs (augmenter `REQUEST_DELAY`)
3. **User-Agent** : Utiliser un User-Agent réaliste
4. **Légalité** : Vérifier les conditions d'utilisation du site
5. **Données personnelles** : Respecter le RGPD

## Dépannage

### Le scraper ne trouve pas les éléments

- Augmenter `IMPLICIT_WAIT` et `PAGE_LOAD_TIMEOUT`
- Utiliser `headless=False` pour voir le navigateur
- Vérifier les sélecteurs CSS avec DevTools
- Ajouter des délais avec `time.sleep()`

### Erreurs de timeout

- Augmenter `PAGE_LOAD_TIMEOUT` dans `.env`
- Vérifier la connexion internet
- Le site peut être lent ou utiliser du JavaScript lourd

### Données incomplètes

- Le contenu peut être chargé dynamiquement
- Essayer `scraper.scroll_to_bottom()` avant extraction
- Vérifier si le contenu est dans un iframe

### Chrome/ChromeDriver ne démarre pas

```bash
# Mettre à jour webdriver-manager
pip install --upgrade webdriver-manager

# Vérifier que Chrome est installé
google-chrome --version  # Linux
# ou
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version  # macOS
```

## Exemples Avancés

### Scraper avec authentification

```python
scraper = WebScraper()
scraper.setup_driver()

# Naviguer vers la page de login
scraper.driver.get('https://example.com/login')

# Remplir le formulaire
from selenium.webdriver.common.by import By

username = scraper.driver.find_element(By.ID, 'username')
password = scraper.driver.find_element(By.ID, 'password')

username.send_keys('your_username')
password.send_keys('your_password')

# Soumettre
submit = scraper.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
submit.click()

time.sleep(3)

# Continuer le scraping
scraper.driver.get('https://example.com/data')
# ...
```

### Scraper avec recherche

```python
scraper = WebScraper()
scraper.setup_driver()
scraper.driver.get('https://example.com')

# Rechercher
search_box = scraper.driver.find_element(By.NAME, 'q')
search_box.send_keys('Python')
search_box.submit()

time.sleep(2)

# Extraire les résultats
data = scraper.extract_page_data(selectors)
```

### Export personnalisé

```python
import json

scraper = WebScraper()
# ... scraping

# Export personnalisé
with open('custom_export.json', 'w', encoding='utf-8') as f:
    json.dump({
        'metadata': {
            'scraped_at': datetime.now().isoformat(),
            'total_items': len(scraper.data)
        },
        'items': scraper.data
    }, f, indent=2, ensure_ascii=False)
```

## Support et Contribution

Pour signaler des bugs ou proposer des améliorations, créez une issue sur le dépôt du projet.

## Licence

MIT License - Utilisation libre avec attribution.

## Avertissement

Cet outil est fourni à des fins éducatives et de recherche. L'utilisateur est responsable de l'utilisation de cet outil et doit respecter les conditions d'utilisation des sites web ciblés ainsi que les lois en vigueur.
