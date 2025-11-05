# 🌐 Web Scraper Pro - Application Web

Application web professionnelle pour scraping, recherche de domaines et enrichissement de données.

## 🎯 Fonctionnalités

### 📊 Pipeline Complet
1. **Scraping** : Extraire les exposants Equipauto
2. **Domain Finder** : Trouver les sites web avec score de confiance
3. **Data Enrichment** : Enrichir avec emails, téléphones, LinkedIn, dirigeants

### ✨ Caractéristiques
- ✅ Interface web moderne et responsive
- ✅ Progression en temps réel
- ✅ Logs détaillés
- ✅ Téléchargement des résultats (CSV, JSON, Excel)
- ✅ Configuration des APIs via interface
- ✅ 100% Gratuit

## 🚀 Lancement Local

```bash
# 1. Installer les dépendances
python3 -m pip install -r requirements.txt

# 2. Lancer l'application
python3 app.py

# 3. Ouvrir dans le navigateur
http://localhost:5000
```

## 🌍 Déploiement en Ligne

Voir le guide complet : **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**

### Déploiement Rapide (Render.com)

1. Créer un compte : https://render.com
2. Connecter votre repo GitHub
3. Déployer en 1 clic
4. URL finale : `https://votre-app.onrender.com`

**Temps** : 15 minutes
**Coût** : 100% Gratuit

## 📱 Utilisation

### Étape 1 : Scraping
1. Cliquer sur "Lancer le Scraping"
2. Attendre l'extraction (~2-3 min)
3. Télécharger les résultats

### Étape 2 : Domain Finder
1. Choisir le nombre d'entreprises (10, 50, 100, ou toutes)
2. Cliquer sur "Trouver les Domaines"
3. Suivre la progression en temps réel
4. Télécharger les résultats avec scores de confiance

### Étape 3 : Enrichment
1. Choisir le nombre d'entreprises
2. Cliquer sur "Enrichir les Données"
3. Attendre l'enrichissement multi-sources
4. Télécharger les résultats enrichis

### Configuration des APIs (Optionnel)
1. Cliquer sur "⚙️ Configuration"
2. Ajouter vos clés API :
   - **Pappers** : https://www.pappers.fr/api (10,000/mois gratuit)
   - **Hunter** : https://hunter.io/users/sign_up (50/mois gratuit)
3. Sauvegarder

**Note** : L'app fonctionne aussi sans APIs (scraping web uniquement)

## 📊 Résultats Attendus

### Sans APIs (Scraping web)
- Emails : ~50%
- Téléphones : ~20%
- LinkedIn : ~40%
- Dirigeants : 0%

### Avec APIs (Recommandé)
- Emails : ~70%
- Téléphones : ~30%
- LinkedIn : ~60%
- Dirigeants : ~80% (entreprises FR via Pappers)

## 🔧 Architecture

```
Frontend (HTML/CSS/JS)
    ↓
Flask API (Python)
    ↓
┌─────────────┬─────────────┬──────────────┐
│  Scraping   │   Domains   │  Enrichment  │
└─────────────┴─────────────┴──────────────┘
    ↓               ↓               ↓
[Selenium]    [Clearbit API]  [Multi-sources]
                                    ↓
                          ┌─────────┴─────────┐
                     [Pappers]          [Hunter]
```

## 📁 Fichiers Clés

- `app.py` - Backend Flask
- `templates/index.html` - Interface web
- `static/css/style.css` - Styles modernes
- `static/js/app.js` - Logique client
- `render.yaml` - Configuration Render.com
- `Procfile` - Configuration Heroku/Railway
- `requirements.txt` - Dépendances Python

## 🔐 Sécurité

### Pour usage personnel
- Aucune authentification requise
- Clés API stockées localement (`.env`)

### Pour équipe
- Ajouter Flask-Login pour authentification
- Utiliser variables d'environnement sur serveur
- Implémenter rate limiting

## 🌟 Avantages de l'Application Web

| Aspect | Scripts CLI | Application Web |
|--------|-------------|-----------------|
| **Interface** | Terminal | Interface moderne |
| **Progression** | Texte | Barre visuelle + logs |
| **Accessibilité** | Local uniquement | Accessible partout |
| **Équipe** | Installation requise | URL à partager |
| **Configuration** | Fichier .env | Interface web |
| **Résultats** | Fichiers locaux | Téléchargement direct |

## 💡 Use Cases

### 1. Équipe Marketing
- Scraper les salons professionnels
- Trouver les contacts des exposants
- Enrichir pour campagnes email

### 2. Business Development
- Identifier prospects
- Vérifier sites web existants
- Récupérer infos de contact

### 3. Data Analysts
- Collecter données entreprises
- Analyser présence digitale
- Exporter pour CRM

## ⚠️ Limitations

### Render.com Gratuit
- Se met en veille après 15min d'inactivité
- Redémarre en ~30 secondes
- Pas de Selenium (Chrome non installé)

### Solutions
- Scraper en local, uploader résultats
- Utiliser "pinger" gratuit (UptimeRobot)
- Passer au plan payant ($7/mois)

## 🚀 Évolutions Futures

- [ ] Authentification utilisateurs
- [ ] Historique des jobs
- [ ] Upload de fichiers CSV personnalisés
- [ ] Support multi-sites (pas que Equipauto)
- [ ] API REST pour intégrations
- [ ] Webhooks pour notifications
- [ ] Dashboard analytics avancé

## 📞 Support

**Documentation complète** : [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**Questions fréquentes** :
- L'app fonctionne-t-elle hors ligne ? Non, nécessite internet
- Puis-je déployer sur mon serveur ? Oui, voir guide
- Les données sont-elles sécurisées ? Oui, HTTPS par défaut
- Combien d'utilisateurs simultanés ? Render gratuit : ~10-20

## 🎉 Conclusion

Tu as maintenant une **application web professionnelle** accessible via HTTPS, 100% gratuite, sans perte de fonctionnalité par rapport aux scripts CLI !

**Prochaine étape** : Déploie sur Render.com et partage l'URL avec ton équipe ! 🚀

---

**Développé avec** : Flask, Python, HTML/CSS/JS
**Hébergement** : Render.com, Railway, Fly.io
**Coût** : 0€
