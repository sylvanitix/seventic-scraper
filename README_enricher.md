# company_enricher.py

Enrichit les données d'entreprises avec contacts et dirigeants.

## 🎯 Données Extraites

### Entreprise
- Email de contact
- Numéro de téléphone
- LinkedIn entreprise
- Adresse légale (si FR)
- SIREN/SIRET (si FR)

### Dirigeants
- Prénom / Nom
- Fonction
- Email (si disponible)
- LinkedIn (si disponible)

## 📊 Sources de Données (Gratuites)

| Source | Limite Gratuite | Données Fournies |
|--------|----------------|------------------|
| **Scraping Web** | Illimité | Emails, téléphones, LinkedIn |
| **Pappers.fr API** | 10,000/mois | Infos légales, dirigeants (FR) |
| **Hunter.io API** | 50/mois | Emails professionnels |

## 🚀 Usage

### Sans clés API (100% gratuit)
```bash
python3 company_enricher.py
```
Utilise uniquement le scraping web.

### Avec clés API (recommandé)

1. Créer un fichier `.env` :
```bash
PAPPERS_API_KEY=votre_clé_pappers
HUNTER_API_KEY=votre_clé_hunter
```

2. Obtenir les clés gratuites :
- **Pappers** : https://www.pappers.fr/api (10,000/mois)
- **Hunter** : https://hunter.io/users/sign_up (50/mois)

3. Exécuter :
```bash
python3 company_enricher.py
```

## ⚙️ Configuration

Modifier ligne 331 pour nombre d'entreprises :
```python
max_results=10  # Ou None pour toutes
```

## 📈 Résultats

**Sans API** (scraping uniquement) :
- Emails : ~50%
- Téléphones : ~20%
- LinkedIn : ~40%
- Dirigeants : 0%

**Avec APIs** (recommandé pour FR) :
- Emails : ~70%
- Téléphones : ~30%
- LinkedIn : ~60%
- Dirigeants : ~80% (entreprises FR)

## 📄 Formats Export

- `company_enriched_data.json` : Complet
- `company_enriched_data.csv` : Simplifié
- `company_enriched_data.xlsx` : Excel

## ⚠️ Notes

- **Respectez les TOS** des sites web
- **Rate limiting** : 1.5s entre requêtes
- **Données publiques** uniquement
- Qualité variable selon entreprises
