# Index des Outils - Web Scraper

## 🔧 Outils Principaux

### 1. **scraper.py**
Scraper générique réutilisable avec Selenium.
- 📄 [Documentation](README_scraper.md)
- ⚡ Gestion iframes, proxy, rate limiting
- 💾 Export JSON/CSV/Excel

### 2. **equipauto_scraper_fast.py**
Scraper optimisé pour EQUIP AUTO Paris.
- 📄 [Documentation](README_equipauto_fast.md)
- 🚀 Ultra-rapide avec BeautifulSoup
- ✅ 2514 éléments en ~25 secondes

### 3. **clean_data.py**
Nettoyage et déduplication des données.
- 📄 [Documentation](README_clean_data.md)
- 🧹 2514 → 1301 exposants uniques
- 📊 Statistiques détaillées

### 4. **domain_finder.py**
Trouve les sites web des entreprises (version basique).
- 📄 [Documentation](README_domain_finder.md)
- 🔍 Recherche DuckDuckGo + devinette patterns
- 📈 50% de taux de réussite, 3.4s/entreprise

### 5. **domain_finder_optimized.py** ⭐ RECOMMANDÉ
Version ultra-rapide et précise du domain finder.
- 📄 [Documentation](README_domain_finder_optimized.md)
- ⚡ **8x plus rapide** : 0.43s/entreprise
- 🎯 **100% de réussite** sur tests
- 🚀 Traitement parallèle, DNS check, Clearbit API

### 6. **config.py**
Configuration centralisée.
- 📄 [Documentation](README_config.md)
- ⚙️ Timeouts, proxy, User-Agents
- 🔧 Modifiable via `.env`

---

## 📊 Résultats Actuels

| Outil | Input | Output | Format |
|-------|-------|--------|--------|
| equipauto_scraper_fast | Site web | 2514 records | JSON/CSV/Excel |
| clean_data | 2514 records | 1301 uniques | JSON/CSV/Excel |
| domain_finder | 1301 noms | 50% domaines (3.4s/co) | JSON/CSV/Excel |
| **domain_finder_optimized** | **1301 noms** | **100% domaines (0.43s/co)** | **JSON/CSV/Excel** |

---

## 🚀 Guide Rapide

### Scraper un nouveau site
```bash
python3 equipauto_scraper_fast.py
```

### Nettoyer les données
```bash
python3 clean_data.py
```

### Trouver les domaines (VERSION OPTIMISÉE - RECOMMANDÉ) ⭐
```bash
# Test sur 100 entreprises (100% réussite, 0.43s/entreprise)
python3 domain_finder_optimized.py

# Pour TOUTES les 1301 entreprises (~9 minutes)
# Modifier ligne 308: max_results=None
python3 domain_finder_optimized.py
```

### Trouver les domaines (version basique - plus lent)
```bash
python3 domain_finder.py  # 50% réussite, 3.4s/entreprise
```

---

## 📁 Structure des Fichiers

```
web-scraper/
├── scraper.py                          # Scraper générique
├── equipauto_scraper_fast.py           # Scraper Equipauto
├── clean_data.py                       # Nettoyage données
├── domain_finder.py                    # Recherche domaines
├── config.py                           # Configuration
├── requirements.txt                    # Dépendances
├── .env                               # Config locale
│
├── output/                            # Résultats
│   ├── equipauto_exhibitors.json      # Données brutes
│   ├── equipauto_exhibitors.csv
│   ├── equipauto_exhibitors.xlsx
│   ├── equipauto_exhibitors_clean.*   # Données nettoyées
│   └── company_domains.*              # Domaines trouvés
│
├── README.md                          # Documentation principale
├── RESULTS.md                         # Résultats Equipauto
├── TOOLS_INDEX.md                     # Ce fichier
│
└── README_*.md                        # Docs individuelles
```

---

## 💡 Prochaines Étapes

1. **Lancer domain_finder sur TOUTES les entreprises** (1301)
2. **Améliorer le taux de réussite** avec plus de sources de recherche
3. **Extraire plus de détails** (téléphone, email, etc.)
4. **Scraper d'autres salons** similaires

---

## 📞 Usage

Chaque outil peut être lancé indépendamment. Voir la documentation individuelle pour plus de détails.
