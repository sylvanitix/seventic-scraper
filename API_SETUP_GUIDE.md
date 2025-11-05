# Guide de Configuration des APIs Gratuites

Ce guide explique comment obtenir et configurer les clés API gratuites pour l'enrichisseur de données.

## 🔑 Pappers.fr API (Recommandé pour entreprises françaises)

### Avantages
- ✅ **10,000 requêtes/mois gratuit**
- ✅ Données légales officielles (INSEE, INPI)
- ✅ Dirigeants avec prénoms/noms/fonctions
- ✅ SIREN/SIRET
- ✅ Adresses complètes

### Inscription

1. **Créer un compte** : https://www.pappers.fr/api
2. **Valider l'email professionnel**
3. **Obtenir la clé API** dans votre dashboard
4. **Ajouter au `.env`** :
```bash
PAPPERS_API_KEY=votre_clé_ici
```

### Exemple de Réponse

```json
{
  "siren": "123456789",
  "nom_entreprise": "ACME SAS",
  "siege": {
    "adresse_ligne_1": "123 Rue de la Paix",
    "code_postal": "75001",
    "ville": "PARIS"
  },
  "representants": [
    {
      "nom": "DUPONT",
      "prenoms": "Jean Pierre",
      "qualite": "Président"
    }
  ]
}
```

### Limites
- ❌ Uniquement entreprises françaises
- ❌ Pas d'emails/téléphones directs
- ❌ LinkedIn non disponible

---

## 📧 Hunter.io API (Pour emails professionnels)

### Avantages
- ✅ **50 recherches/mois gratuit**
- ✅ Emails professionnels vérifiés
- ✅ Score de confiance
- ✅ International

### Inscription

1. **Créer un compte** : https://hunter.io/users/sign_up
2. **Valider l'email**
3. **Obtenir la clé API** : https://hunter.io/api_keys
4. **Ajouter au `.env`** :
```bash
HUNTER_API_KEY=votre_clé_ici
```

### Exemple de Réponse

```json
{
  "emails": [
    {
      "value": "contact@example.com",
      "type": "generic",
      "confidence": 95,
      "first_name": "John",
      "last_name": "Doe",
      "position": "CEO"
    }
  ]
}
```

### Limites
- ❌ Seulement 50/mois sur free tier
- ❌ Limité à 10 résultats par recherche
- ❌ Pas d'infos légales

### Stratégie d'Usage
**Utilisez Hunter uniquement si :**
- Email non trouvé par scraping web
- Besoin de matcher emails avec dirigeants
- Entreprise importante (prioriser)

---

## 🔧 Configuration du Fichier .env

Créer un fichier `.env` à la racine du projet :

```bash
# Pappers.fr API (10,000/mois gratuit)
PAPPERS_API_KEY=votre_clé_pappers_ici

# Hunter.io API (50/mois gratuit)
HUNTER_API_KEY=votre_clé_hunter_ici
```

**Important** : Ne jamais commit le fichier `.env` sur Git !

---

## 📊 Stratégie d'Utilisation Optimale

### Scénario 1 : Sans Budget (0€)
```
Scraping Web uniquement
→ 50% emails, 20% téléphones, 40% LinkedIn
→ Illimité, gratuit
```

### Scénario 2 : Entreprises Françaises (0€)
```
1. Scraping Web
2. Pappers.fr (10,000/mois)
→ 70% emails, 30% téléphones, 80% dirigeants
```

### Scénario 3 : Optimal Gratuit (0€)
```
1. Scraping Web (tous)
2. Pappers.fr (entreprises FR)
3. Hunter.io (50 entreprises prioritaires)
→ ~75% emails, ~35% téléphones, ~85% dirigeants
```

---

## 🎯 Recommandations

### Pour 50 entreprises ou moins
✅ Utilisez Hunter.io + Pappers.fr
→ Résultats maximums

### Pour 50-10,000 entreprises
✅ Utilisez Pappers.fr uniquement
→ Bon équilibre qualité/quantité

### Pour 10,000+ entreprises
✅ Scraping Web uniquement
→ Illimité mais qualité moindre

---

## ⚠️ Limites et Respect des TOS

### Légal
- ✅ Données publiques uniquement
- ✅ Scraping respectueux (rate limiting)
- ✅ APIs officielles avec TOS acceptés

### Éthique
- ❌ Ne pas abuser des APIs gratuites
- ❌ Ne pas revendre les données
- ❌ Respecter le RGPD

### Technique
- ⏱️ Rate limiting : 1.5s entre requêtes
- 🔄 Retry logic en cas d'erreur
- 💾 Cache pour éviter requêtes dupliquées

---

## 🆘 Dépannage

### "No API key found"
→ Vérifiez que le fichier `.env` existe
→ Vérifiez le nom des variables (majuscules)

### "API quota exceeded"
→ Pappers : Attendez le mois suivant
→ Hunter : Passez au plan payant ou attendez

### "No data found"
→ Normal pour ~30% des entreprises
→ Site web sans infos publiques
→ Entreprise étrangère (Pappers)

---

## 📈 Monitoring de l'Usage

L'enrichisseur affiche automatiquement :

```
API Usage:
  • Websites scraped: 50
  • Pappers API calls: 45
  • Hunter API calls: 12
```

Suivez votre consommation pour rester dans les limites gratuites !
