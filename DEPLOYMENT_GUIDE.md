# 🚀 Guide de Déploiement - Web Scraper Pro

Guide complet pour déployer l'application web sur différentes plateformes **100% GRATUITES**.

---

## 📋 Table des Matières

1. [Test Local](#test-local)
2. [Déploiement sur Render.com (Recommandé)](#déploiement-sur-rendercom)
3. [Déploiement sur Railway](#déploiement-sur-railway)
4. [Déploiement sur Fly.io](#déploiement-sur-flyio)
5. [Configuration des APIs](#configuration-des-apis)
6. [Dépannage](#dépannage)

---

## ✅ Test Local

Avant de déployer, testez l'application localement :

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'application
python app.py

# 3. Ouvrir dans le navigateur
http://localhost:5000
```

Si tout fonctionne → Passez au déploiement en ligne !

---

## 🌟 Déploiement sur Render.com (RECOMMANDÉ)

### Pourquoi Render.com ?
- ✅ 100% Gratuit
- ✅ HTTPS automatique
- ✅ Déploiement en 5 minutes
- ✅ Pas de carte bancaire requise
- ✅ Interface ultra simple

### Étape 1 : Préparer le Code

1. **Créer un compte GitHub** (si pas déjà fait) : https://github.com/signup

2. **Créer un nouveau dépôt** :
   - Nom : `web-scraper-pro`
   - Public ou Privé (au choix)
   - Ne pas initialiser avec README

3. **Pousser le code sur GitHub** :
```bash
cd /Users/sylvainboue/web-scraper
git init
git add .
git commit -m "Initial commit - Web Scraper Pro"
git branch -M main
git remote add origin https://github.com/TON-USERNAME/web-scraper-pro.git
git push -u origin main
```

### Étape 2 : Déployer sur Render

1. **Créer un compte Render** : https://render.com/
   - Inscription gratuite
   - Connecter avec GitHub (recommandé)

2. **Créer un nouveau Web Service** :
   - Cliquer sur "New +" → "Web Service"
   - Sélectionner le dépôt `web-scraper-pro`
   - Cliquer sur "Connect"

3. **Configuration** :
   - **Name** : `web-scraper-pro` (ou votre choix)
   - **Region** : Choisir la plus proche
   - **Branch** : `main`
   - **Runtime** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app`
   - **Instance Type** : `Free` ✅

4. **Variables d'environnement** (Optionnel - configurable plus tard) :
   - Cliquer sur "Advanced"
   - Ajouter :
     ```
     PAPPERS_API_KEY = votre_clé
     HUNTER_API_KEY = votre_clé
     ```

5. **Déployer** :
   - Cliquer sur "Create Web Service"
   - Attendre 5-10 minutes (première fois)
   - ✅ Votre app sera disponible à : `https://web-scraper-pro.onrender.com`

### Étape 3 : Configurer les APIs

1. Ouvrir votre app : `https://web-scraper-pro.onrender.com`
2. Cliquer sur "⚙️ Configuration"
3. Ajouter vos clés API Pappers et Hunter
4. Cliquer sur "Sauvegarder"

### 🎉 Terminé ! Votre équipe peut maintenant accéder à l'outil !

---

## 🚂 Déploiement sur Railway

Alternative gratuite à Render.

### Étapes :

1. **Créer un compte** : https://railway.app/
2. **Nouveau Projet** → "Deploy from GitHub repo"
3. **Sélectionner** `web-scraper-pro`
4. Railway détecte automatiquement Python
5. **Ajouter variables d'environnement** :
   - Settings → Variables
   - Ajouter `PAPPERS_API_KEY` et `HUNTER_API_KEY`
6. **Déployer** automatiquement
7. **Générer domaine** : Settings → Generate Domain

URL finale : `https://web-scraper-pro.up.railway.app`

**Limite gratuite** : 500 heures/mois (suffisant pour petite équipe)

---

## ✈️ Déploiement sur Fly.io

Pour utilisateurs avancés.

### Étapes :

1. **Installer Fly CLI** :
```bash
curl -L https://fly.io/install.sh | sh
```

2. **Se connecter** :
```bash
flyctl auth login
```

3. **Lancer l'app** :
```bash
cd /Users/sylvainboue/web-scraper
flyctl launch
```

4. **Configurer** :
   - App name : `web-scraper-pro`
   - Region : Choisir la plus proche
   - PostgreSQL : Non
   - Redis : Non

5. **Définir secrets** :
```bash
flyctl secrets set PAPPERS_API_KEY=votre_clé
flyctl secrets set HUNTER_API_KEY=votre_clé
```

6. **Déployer** :
```bash
flyctl deploy
```

URL finale : `https://web-scraper-pro.fly.dev`

---

## 🔑 Configuration des APIs

### Pappers.fr (Recommandé pour entreprises françaises)

1. **S'inscrire** : https://www.pappers.fr/api
2. **Obtenir la clé** : Dashboard → API Key
3. **Ajouter dans l'app** : Configuration → Pappers API Key

### Hunter.io (Emails professionnels)

1. **S'inscrire** : https://hunter.io/users/sign_up
2. **Obtenir la clé** : https://hunter.io/api_keys
3. **Ajouter dans l'app** : Configuration → Hunter API Key

### Sans APIs (Mode gratuit basique)

L'app fonctionne aussi **sans aucune clé API** :
- ✅ Scraping : 100% fonctionnel
- ✅ Domain Finder : Clearbit gratuit (pas de clé requise)
- ✅ Enrichment : Scraping web uniquement
- ⚠️ Moins de données (pas d'infos légales, moins d'emails)

---

## 🛠️ Dépannage

### Problème : L'app se met en veille

**Render.com gratuit** : L'app se met en veille après 15min d'inactivité.

**Solutions** :
1. Accepter 30sec de démarrage au premier accès
2. Utiliser un "pinger" gratuit : https://uptimerobot.com/
3. Passer au plan payant Render ($7/mois)

### Problème : Timeout lors du scraping

**Cause** : Render limite à 30 secondes par requête HTTP.

**Solutions** :
1. L'app utilise du threading (pas affecté)
2. Les jobs tournent en arrière-plan
3. Rafraîchir la page pendant le job

### Problème : Erreur de déploiement

**Vérifier** :
1. `requirements.txt` est bien présent
2. `Procfile` est bien présent
3. `runtime.txt` spécifie Python 3.11

**Commandes de debug** :
```bash
# Voir les logs Render
# Dashboard → Web Service → Logs

# Tester localement
python app.py
```

### Problème : APIs ne fonctionnent pas

**Vérifier** :
1. Clés API bien enregistrées (Configuration)
2. Clés valides (tester sur sites officiels)
3. Quotas non dépassés

### Problème : Selenium ne fonctionne pas en production

**Note** : Selenium (scraping) ne fonctionne PAS sur les plateformes gratuites car Chrome n'est pas installé.

**Solutions** :
1. **Option A** : Scraper en local, uploader les résultats
2. **Option B** : Utiliser scrapers sans Selenium (BeautifulSoup uniquement)
3. **Option C** : Déployer sur serveur avec Chrome (DigitalOcean, AWS)

**Pour Equipauto spécifiquement** :
- Scraper en local une fois
- Uploader `equipauto_exhibitors_clean.json` dans l'app
- Utiliser Domain Finder et Enrichment online

---

## 📊 Comparaison des Plateformes

| Plateforme | Gratuit | HTTPS | Facile | Selenium | Limite |
|------------|---------|-------|--------|----------|--------|
| **Render** | ✅ | ✅ | ⭐⭐⭐ | ❌ | Sleep après 15min |
| **Railway** | ✅ | ✅ | ⭐⭐ | ❌ | 500h/mois |
| **Fly.io** | ✅ | ✅ | ⭐ | ❌ | 3 apps max |
| **Heroku** | ❌ | ✅ | ⭐⭐⭐ | ❌ | Payant ($7/mois) |
| **DigitalOcean** | ❌ | ✅ | ⭐ | ✅ | $5/mois |

**Recommandation** : Render.com pour débuter !

---

## 🎯 Workflow Recommandé pour Équipe

### Pour 100% gratuit :

1. **Scraping** : Faire en local (Selenium fonctionne)
2. **Uploader** : Mettre les JSON dans l'app déployée
3. **Domain Finder** : Utiliser l'app en ligne
4. **Enrichment** : Utiliser l'app en ligne avec APIs

### Pour production (petit budget) :

1. **Serveur DigitalOcean** : $5/mois
2. **Tout fonctionne** : Scraping + Domain + Enrichment
3. **Chrome installé** : Selenium opérationnel
4. **URL personnalisée** : `https://scraper.ton-entreprise.com`

---

## 🔐 Sécurité

### Pour usage en équipe :

1. **Ajouter authentification** (optionnel) :
   - Implémenter Flask-Login
   - Créer comptes utilisateurs
   - Protéger les routes

2. **Variables d'environnement** :
   - Ne jamais commit les clés API
   - Utiliser `.env` local
   - Variables d'env sur plateforme de déploiement

3. **Rate limiting** :
   - Implémenter Flask-Limiter
   - Limiter requêtes par IP

---

## 📞 Support

**Questions ?**
- Render Docs : https://render.com/docs
- Railway Docs : https://docs.railway.app
- Fly Docs : https://fly.io/docs

**Problèmes spécifiques à l'app ?**
- Vérifier les logs de déploiement
- Tester en local d'abord
- Vérifier les variables d'environnement

---

## ✅ Checklist de Déploiement

- [ ] Code sur GitHub
- [ ] Compte Render.com créé
- [ ] Web Service créé et déployé
- [ ] URL fonctionnelle (ex: https://web-scraper-pro.onrender.com)
- [ ] Clés API Pappers ajoutées (optionnel)
- [ ] Clés API Hunter ajoutées (optionnel)
- [ ] Test complet : Scraping → Domains → Enrichment
- [ ] URL partagée avec l'équipe

**Temps estimé** : 15-20 minutes pour premier déploiement

---

## 🎉 Félicitations !

Votre équipe a maintenant accès à un outil professionnel de scraping et enrichissement de données, 100% gratuit, accessible via HTTPS depuis n'importe où !

**URL à partager** : `https://TON-APP.onrender.com`

Happy Scraping! 🚀
