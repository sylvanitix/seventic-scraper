# 🚀 Pipeline Intégré de Génération de Leads

Un outil puissant qui automatise toute la chaîne de génération de leads en **une seule commande**.

## ✨ Ce que fait le pipeline

```
URL → Scraper → Noms d'entreprises → Domain Finder → Domaines → Enricher → Données de contact
```

**Tout se passe en mémoire** : pas de fichiers CSV intermédiaires à gérer !

---

## 🎯 Utilisation

### 1️⃣ En ligne de commande (Simple et rapide)

```bash
# Exemple basique
python3 lead_pipeline.py https://example.com/exhibitors

# Avec options
python3 lead_pipeline.py https://example.com/exhibitors \
  --max-pages 10 \
  --output output/mes_leads

# Voir toutes les options
python3 lead_pipeline.py --help
```

**Résultat :**
- `output/mes_leads.csv` - Format tableur
- `output/mes_leads.xlsx` - Excel
- `output/mes_leads.json` - JSON complet avec toutes les données

---

### 2️⃣ Via l'interface web

```bash
# Démarrer le serveur
python3 app.py
```

Puis ouvrez : `http://localhost:5000`

**Deux modes disponibles :**

#### Mode Pipeline Complet (Nouveau !)
1. Collez l'URL du site d'exposants
2. Cliquez sur "Run Full Pipeline"
3. Attendez que tout se termine
4. Téléchargez vos résultats

#### Mode Étape par Étape (Pour plus de contrôle)
1. **Scrape** → Récupère les noms d'entreprises
2. **Find Domains** → Trouve les domaines
3. **Enrich** → Enrichit avec emails, téléphones, LinkedIn
4. **Export** → Télécharge aux formats CSV/Excel/JSON

---

## 📊 Ce que vous obtenez

Pour chaque entreprise trouvée :

| Colonne | Description |
|---------|-------------|
| `company_name` | Nom de l'entreprise |
| `domain` | Site web (ex: `exemple.fr`) |
| `email` | Email de contact |
| `phone` | Téléphone |
| `linkedin` | Page LinkedIn entreprise |
| `address` | Adresse (si disponible) |
| `city` | Ville |
| `siren` | N° SIREN (entreprises françaises) |
| `siret` | N° SIRET (entreprises françaises) |
| `executive_first_name` | Prénom du dirigeant |
| `executive_last_name` | Nom du dirigeant |
| `executive_role` | Fonction |
| `executive_email` | Email du dirigeant |
| `executive_linkedin` | LinkedIn du dirigeant |
| `data_sources` | Sources des données |

---

## 🔧 Configuration (Optionnel)

Pour de meilleurs résultats, ajoutez des clés API **gratuites** :

### 1. Pappers (pour les entreprises françaises)
- Inscrivez-vous : https://www.pappers.fr/api
- 10 000 requêtes/mois **GRATUITES**
- Donne : SIREN, SIRET, dirigeants, adresses

### 2. Hunter.io (pour les emails)
- Inscrivez-vous : https://hunter.io/users/sign_up
- 50 requêtes/mois **GRATUITES**
- Donne : emails des dirigeants

### Configuration

Créez un fichier `.env` :

```bash
PAPPERS_API_KEY=votre_clé_pappers
HUNTER_API_KEY=votre_clé_hunter
```

**Sans clés API :** Le système fonctionne quand même en scrappant les sites web directement.

---

## 💡 Exemples d'utilisation

### Exemple 1 : Salon Equipauto
```bash
python3 lead_pipeline.py "https://new-liste-exposants.hubj2c.com/" --max-pages 10
```

### Exemple 2 : N'importe quel salon/annuaire
```bash
python3 lead_pipeline.py "https://votre-salon.com/exposants" --max-pages 5
```

### Exemple 3 : En Python (pour intégration)
```python
from lead_pipeline import LeadPipeline

# Créer le pipeline
pipeline = LeadPipeline()

# Exécuter
results = pipeline.run(
    url="https://example.com/exhibitors",
    max_pages=10,
    export_csv=True,
    output_prefix="output/my_leads"
)

# Accéder aux résultats
print(f"Entreprises trouvées : {results['stats']['total_companies_scraped']}")
print(f"Domaines trouvés : {results['stats']['domains_found']}")
print(f"Emails trouvés : {results['stats']['emails_found']}")

# Les données enrichies
for company in results['companies_enriched']:
    print(f"{company['company_name']} - {company['company_email']}")
```

---

## 🎨 Architecture

Le pipeline utilise **3 modules optimisés** :

### 1. `universal_scraper.py`
- Scrape n'importe quel site web
- Détection automatique des entreprises
- Gestion automatique de la pagination
- Pas besoin de code spécifique par site

### 2. `domain_finder.py`
- Trouve les domaines via Clearbit (gratuit)
- Validation intelligente (détecte les domaines parkés)
- Score de confiance pour chaque domaine
- Taux de faux positifs estimé

### 3. `company_enricher.py`
- Scrape les pages de contact
- APIs Pappers + Hunter (optionnelles)
- Emails, téléphones, LinkedIn
- Données des dirigeants

### 4. `lead_pipeline.py` ⭐ (NOUVEAU)
- **Orchestre les 3 modules**
- Tout en mémoire (rapide)
- Export optionnel à la fin
- Progress tracking en temps réel

---

## ⚡ Performance

| Métrique | Valeur |
|----------|--------|
| Vitesse | ~3-5 secondes par entreprise |
| Taux de succès domaines | 60-80% |
| Taux de succès emails | 40-60% |
| Taux de succès téléphones | 30-50% |

**Exemple pour 100 entreprises :**
- Temps total : ~10-15 minutes
- Domaines trouvés : ~60-80
- Emails trouvés : ~30-50

---

## 🚨 Limites et bonnes pratiques

### Limites
- Fonctionne mieux avec des sites structurés (salons, annuaires)
- Nécessite une connexion internet stable
- Les clés API gratuites ont des quotas

### Bonnes pratiques
1. **Commencez petit** : Testez avec `--max-pages 2` d'abord
2. **Vérifiez les résultats** : Les domaines avec confiance < 70% peuvent être faux
3. **Respectez les quotas** : Pappers = 10k/mois, Hunter = 50/mois
4. **Soyez patient** : Le scraping prend du temps pour être respectueux

---

## 🐛 Dépannage

### Problème : "No companies found"
- Vérifiez que l'URL contient bien une liste d'entreprises
- Le site peut utiliser du JavaScript lourd (le scraper gère Selenium)

### Problème : "Peu de domaines trouvés"
- Normal ! Certaines entreprises n'ont pas de site web
- Essayez d'ajouter la clé Pappers pour les entreprises françaises

### Problème : "Peu d'emails trouvés"
- Normal aussi ! Beaucoup de sites cachent les emails
- Ajoutez la clé Hunter pour améliorer

### Problème : Le scraper est lent
- C'est normal, il faut être respectueux des serveurs
- On attend 1-2 secondes entre chaque requête

---

## 📝 Fichiers du projet

```
web-scraper/
├── lead_pipeline.py          ⭐ Pipeline intégré (NOUVEAU)
├── universal_scraper.py      🌐 Scraper universel
├── domain_finder.py          🔍 Chercheur de domaines
├── company_enricher.py       💼 Enrichisseur de données
├── app.py                    🖥️  Interface web
├── requirements.txt          📦 Dépendances
├── .env.example              🔐 Exemple de config
└── output/                   📁 Résultats exportés
```

---

## 🎁 Avantages vs l'ancienne méthode

| Ancienne méthode | Nouvelle méthode (Pipeline) |
|------------------|----------------------------|
| 3 commandes séparées | 1 seule commande |
| Fichiers CSV intermédiaires | Tout en mémoire |
| Import/Export manuel | Automatique |
| Configuration par site | Universel |
| ~20 minutes de manip | ~2 minutes de manip |

---

## 🤝 Contribution

Ce pipeline est modulaire :
- Modifiez `universal_scraper.py` pour améliorer la détection
- Modifiez `domain_finder.py` pour ajouter des sources
- Modifiez `company_enricher.py` pour plus de données

Chaque module fonctionne indépendamment ET ensemble !

---

## 📞 Support

Questions ? Problèmes ?
- Consultez les logs détaillés dans le terminal
- Vérifiez le fichier `.env` pour les clés API
- Testez chaque module individuellement pour débugger

---

**Fait avec ❤️ pour simplifier la génération de leads**
