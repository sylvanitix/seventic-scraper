# domain_finder.py

Trouve les domaines des entreprises avec scoring de confiance et taux de faux positifs.

## 🎯 Caractéristiques

- **Clearbit API gratuite** (autocomplete + logo)
- **Validation stricte** anti-domaines parkés
- **Score de confiance** (0-100%)
- **Taux de faux positifs estimé** (5-40%)
- **Tri par fiabilité**

## 📊 Colonnes Exportées

| Colonne | Description |
|---------|-------------|
| `company_name` | Nom de l'entreprise |
| `domain` | Domaine trouvé |
| `confidence_score` | Score 0-100% |
| `confidence_label` | "Très élevée", "Élevée", "Moyenne" |
| `false_positive_rate` | Probabilité d'erreur (5%, 15%, 40%) |
| `method` | Méthode de détection |
| `clearbit_name` | Nom selon Clearbit |

## 🚀 Usage

```bash
python3 domain_finder.py
```

Modifier ligne 227 pour nombre d'entreprises :
```python
max_results=30  # Ou None pour toutes
```

## ⚠️ Interprétation des Scores

### Très Élevée (≥90%)
- **Faux positif**: ~5%
- **Action**: Accepter avec confiance
- **Exemple**: 3M France → 3mfrance.fr

### Élevée (70-90%)
- **Faux positif**: ~15%
- **Action**: Vérifier rapidement
- **Exemple**: 2AB → abebooks.com (FAUX!)

### Moyenne (50-70%)
- **Faux positif**: ~40%
- **Action**: VALIDATION MANUELLE OBLIGATOIRE
- **Exemple**: A+GLASS → glasschutzfolien.ch

## 💡 Recommandation

**Toujours valider manuellement les résultats avec confiance < 90%**
