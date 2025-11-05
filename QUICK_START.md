# ⚡ Quick Start - Web Scraper Pro

Déploiement ultra-rapide en 3 étapes.

## 🎯 Option 1 : Test Local (2 minutes)

```bash
# 1. Installer
python3 -m pip install -r requirements.txt

# 2. Lancer
python3 app.py

# 3. Ouvrir
http://localhost:5000
```

✅ **Terminé !** L'app tourne sur ton ordinateur.

---

## 🌐 Option 2 : Déploiement en Ligne (15 minutes)

### Prérequis
- Compte GitHub (gratuit)
- Compte Render.com (gratuit)

### Étapes

**1. Mettre le code sur GitHub**

```bash
cd /Users/sylvainboue/web-scraper
git init
git add .
git commit -m "Web Scraper Pro"
git branch -M main
git remote add origin https://github.com/TON-USERNAME/web-scraper-pro.git
git push -u origin main
```

**2. Déployer sur Render**

1. Aller sur : https://render.com/
2. Cliquer sur "Get Started for Free"
3. Se connecter avec GitHub
4. Cliquer sur "New +" → "Web Service"
5. Sélectionner le repo `web-scraper-pro`
6. Configuration automatique détectée ✅
7. Cliquer sur "Create Web Service"
8. Attendre 5-10 minutes

**3. C'est prêt !**

Ton app est disponible à : `https://web-scraper-pro.onrender.com`

---

## 🔑 Configuration APIs (Optionnel)

### Dans l'application web

1. Ouvrir `https://ton-app.onrender.com`
2. Cliquer sur "⚙️ Configuration"
3. Ajouter les clés :
   - **Pappers** : https://www.pappers.fr/api
   - **Hunter** : https://hunter.io/users/sign_up
4. Sauvegarder

**Sans APIs** : L'app fonctionne quand même (scraping web uniquement)

---

## 📊 Utilisation

### Pipeline complet :

1. **Scraping** → Extraire les entreprises
2. **Domain Finder** → Trouver les sites web
3. **Enrichment** → Récupérer emails/téléphones/LinkedIn

### Résultats :

Télécharger directement depuis l'interface :
- CSV (Excel)
- JSON (données complètes)
- XLSX (Excel formaté)

---

## 🎉 C'est tout !

Tu as maintenant :
- ✅ Une application web moderne
- ✅ Accessible via HTTPS
- ✅ 100% gratuite
- ✅ Partageable avec ton équipe

**URL à partager** : `https://ton-app.onrender.com`

---

## 🆘 Besoin d'aide ?

- **Guide complet** : [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Documentation** : [README_WEBAPP.md](README_WEBAPP.md)
- **Logs Render** : Dashboard → Logs

---

Happy Scraping! 🚀
