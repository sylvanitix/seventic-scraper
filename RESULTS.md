# Résultats du Scraping Equipauto

## Résumé

Scraping réussi de la liste des exposants du salon **EQUIP AUTO Paris 2025**.

## Statistiques

- **Total d'exposants extraits**: 1301 exposants uniques
- **Format d'export**: JSON, CSV, Excel
- **Données extraites**:
  - Nom de l'exposant
  - Stand (si disponible)
  - Liens (si disponibles)
  - Classes CSS (pour référence)

## Fichiers Générés

### Fichiers Nettoyés (Recommandés)
- `output/equipauto_exhibitors_clean.json` - 165 KB
- `output/equipauto_exhibitors_clean.csv` - 61 KB
- `output/equipauto_exhibitors_clean.xlsx` - 49 KB

### Fichiers Bruts (avec doublons)
- `output/equipauto_exhibitors.json` - 254 KB
- `output/equipauto_exhibitors.csv` - 118 KB
- `output/equipauto_exhibitors.xlsx` - 71 KB

### Fichiers d'Inspection
- `equipauto_page.html` - Code source de la page
- `equipauto_raw.json` - Échantillon des 10 premiers enregistrements

## Exemples d'Exposants

Voici quelques exposants extraits :

1. **2AB**
2. **31 INCORPORATED**
3. **360 WASH FRANCE**
4. **3M France**
5. **4B DISTRIB**
6. **A+GLASS**
7. **ABAC Compresseurs**
8. **ABAKUS**
... et 1293 autres

## Comment Utiliser les Données

### JSON
```python
import json

with open('output/equipauto_exhibitors_clean.json', 'r', encoding='utf-8') as f:
    exhibitors = json.load(f)

# Afficher les 5 premiers
for exhibitor in exhibitors[:5]:
    print(f"- {exhibitor['name']}")
```

### CSV avec Pandas
```python
import pandas as pd

df = pd.read_csv('output/equipauto_exhibitors_clean.csv')
print(df.head(10))

# Rechercher un exposant
search = df[df['name'].str.contains('3M', case=False)]
print(search)
```

### Excel
Ouvrez directement le fichier `equipauto_exhibitors_clean.xlsx` dans Excel, LibreOffice ou Google Sheets.

## Comment Relancer le Scraping

```bash
cd /Users/sylvainboue/web-scraper

# Scraper rapide (recommandé)
python3 equipauto_scraper_fast.py

# Nettoyer les données
python3 clean_data.py
```

## Améliorations Possibles

Le scraper actuel extrait les noms des exposants. Pour obtenir plus d'informations, il faudrait :

1. **Cliquer sur chaque exposant** pour accéder aux détails complets
2. **Extraire des informations supplémentaires** :
   - Numéro de stand/hall
   - Catégorie/secteur d'activité
   - Adresse de l'entreprise
   - Téléphone
   - Email
   - Site web
   - Description des produits
   - Marques représentées

## Code Source

- `scraper.py` - Scraper générique réutilisable
- `equipauto_scraper_fast.py` - Scraper optimisé pour Equipauto
- `clean_data.py` - Script de nettoyage des données
- `config.py` - Configuration

## Performance

- Temps d'exécution : ~25 secondes
- Navigateur : Chrome automatisé avec Selenium
- Gestion automatique :
  - Acceptation des cookies
  - Passage du mode carte au mode liste
  - Parsing rapide avec BeautifulSoup
  - Déduplication automatique

## Date de Scraping

04 novembre 2025 - 14:41
