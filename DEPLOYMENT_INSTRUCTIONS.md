# 🚀 Guide de Déploiement - Seventic Scraper

## Déploiement GRATUIT sur Render.com

### Étape 1: Créer un compte GitHub (si vous n'en avez pas)

1. Allez sur https://github.com
2. Cliquez sur "Sign up" et créez un compte gratuit
3. Vérifiez votre email

### Étape 2: Pousser votre code sur GitHub

Dans votre terminal, exécutez ces commandes:

```bash
# Créer un nouveau repository sur GitHub.com d'abord:
# 1. Allez sur https://github.com/new
# 2. Nom du repository: "seventic-scraper"
# 3. Laissez-le PUBLIC
# 4. NE cochez PAS "Initialize with README"
# 5. Cliquez "Create repository"

# Puis dans votre terminal:
cd /Users/sylvainboue/web-scraper
git remote add origin https://github.com/VOTRE-USERNAME/seventic-scraper.git
git branch -M main
git push -u origin main
```

### Étape 3: Créer un compte Render.com

1. Allez sur https://render.com
2. Cliquez sur "Get Started for Free"
3. Connectez-vous avec votre compte GitHub (recommandé)

### Étape 4: Déployer l'application

1. **Dans le dashboard Render:**
   - Cliquez sur "New +"
   - Sélectionnez "Web Service"

2. **Connecter votre repository:**
   - Cherchez "seventic-scraper"
   - Cliquez "Connect"

3. **Configuration (Render détectera automatiquement les paramètres):**
   - **Name**: seventic-scraper
   - **Region**: Frankfurt (EU Central) - Plus proche de vous
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: FREE

4. **Cliquez sur "Create Web Service"**

### Étape 5: Attendre le déploiement

- Le premier déploiement prend 2-5 minutes
- Vous verrez les logs en temps réel
- Quand vous voyez "Your service is live", c'est prêt!

### Étape 6: Accéder à votre application

Votre URL sera:
```
https://seventic-scraper.onrender.com
```

Partagez cette URL avec vos collaborateurs!

---

## ⚠️ Important - Plan GRATUIT

**Limitations du plan gratuit Render:**
- ✅ Illimité en nombre d'utilisateurs
- ✅ HTTPS inclus
- ✅ Déploiement automatique depuis GitHub
- ⚠️ L'application se met en veille après 15 minutes d'inactivité
- ⚠️ Le premier accès après mise en veille prend 30-60 secondes
- ⚠️ 750 heures/mois (suffisant pour usage d'entreprise)

**Pour garder l'app toujours active (optionnel - $7/mois):**
- Passer au plan "Starter" dans les settings

---

## 🔄 Mettre à jour l'application

Après chaque modification du code:

```bash
cd /Users/sylvainboue/web-scraper
git add .
git commit -m "Description des changements"
git push
```

Render déploiera automatiquement la nouvelle version en 2-3 minutes.

---

## 🛠️ Configuration des API (après déploiement)

1. Accédez à votre application déployée
2. Cliquez sur l'icône ⚙️ "Configuration" dans la barre latérale
3. Entrez vos clés API:
   - **Pappers.fr**: Pour trouver les domaines
   - **Hunter.io**: Pour trouver les emails

Les clés sont stockées dans les cookies du navigateur (chaque utilisateur configure les siennes).

---

## 📞 Support

Si vous rencontrez des problèmes:
1. Vérifiez les logs dans le dashboard Render
2. Assurez-vous que toutes les dépendances sont dans requirements.txt
3. Vérifiez que le port est bien configuré (Render gère ça automatiquement)

---

## ✅ Checklist de déploiement

- [ ] Compte GitHub créé
- [ ] Repository "seventic-scraper" créé sur GitHub
- [ ] Code poussé sur GitHub (`git push`)
- [ ] Compte Render.com créé
- [ ] Web Service créé et connecté au repository
- [ ] Application déployée et accessible
- [ ] URL partagée avec les collaborateurs
- [ ] Clés API configurées

**Votre application sera accessible 24/7 gratuitement!** 🎉
