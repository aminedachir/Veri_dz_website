# VeriDz — Plateforme de Vérification des Actualités 🇩🇿

Plateforme algérienne de fact-checking et détection de fausses informations, propulsée par l'IA.

---

## 🚀 Installation rapide

### 1. Cloner et préparer l'environnement

```bash
cd news_verifier
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 2. Configurer la clé API (optionnel mais recommandé)

```bash
export ANTHROPIC_API_KEY="sk-ant-votre-cle-ici"
```

> Sans clé API, le système fonctionne en **mode démo** avec des réponses simulées.

### 3. Base de données et données initiales

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata initial_categories   # optionnel
```

### 4. Lancer le serveur

```bash
python manage.py runserver
```

Ouvrir : **http://127.0.0.1:8000/**

---

## 📁 Structure du projet

```
news_verifier/
├── manage.py
├── requirements.txt
├── static/
│   └── images/
│       └── logo.jpeg              ← Logo VeriDz
├── templates/
│   └── base.html                  ← Template de base (navbar, footer)
│
├── news_verifier/                 ← Config principale
│   ├── settings.py
│   └── urls.py
│
├── core/                          ← Page d'accueil
│   ├── views.py
│   ├── urls.py
│   └── templates/core/home.html
│
├── news/                          ← Actualités
│   ├── models.py    (Article, Category)
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── templates/news/
│       ├── article_list.html
│       └── article_detail.html
│
├── factcheck/                     ← Vérification IA
│   ├── models.py    (FactCheckResult)
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── ai_service.py              ← Intégration Claude API
│   └── templates/factcheck/
│       ├── factcheck.html
│       └── history.html
│
├── accounts/                      ← Authentification
│   ├── models.py    (User custom)
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── templates/accounts/
│       ├── login.html
│       ├── signup.html
│       └── profile.html
│
└── dashboard/                     ← Espace journaliste
    ├── views.py
    ├── forms.py
    ├── urls.py
    └── templates/dashboard/
        ├── dashboard.html
        └── article_form.html
```

---

## 🌐 URLs disponibles

| URL | Description |
|-----|-------------|
| `/` | Page d'accueil |
| `/news/` | Liste des actualités |
| `/news/<id>/` | Détail d'un article |
| `/fact-check/` | Vérification IA |
| `/fact-check/history/` | Historique des vérifications |
| `/accounts/login/` | Connexion |
| `/accounts/signup/` | Inscription |
| `/accounts/logout/` | Déconnexion |
| `/accounts/profile/` | Profil utilisateur |
| `/dashboard/` | Dashboard journaliste |
| `/dashboard/article/new/` | Créer un article |
| `/dashboard/article/<id>/edit/` | Modifier un article |
| `/admin/` | Panneau d'administration Django |

---

## 🤖 Intégration Claude AI

Le fichier `factcheck/ai_service.py` gère l'appel à l'API Anthropic.

**Mode démo** (sans clé) : réponses simulées basées sur des heuristiques simples.

**Mode réel** (avec clé) : analyse complète par Claude Sonnet avec :
- Verdict (Vrai / Faux / Trompeur / Partiel / Non vérifiable)
- Score de confiance (0–100%)
- Explication détaillée
- Affirmations clés identifiées
- Signaux d'alerte
- Sources recommandées

Pour configurer la clé dans Django (production), utilisez les variables d'environnement :
```python
# settings.py
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
```

---

## 🎨 Design

- **Couleurs** : Bleu marine profond (#060c1f), bleu électrique (#2563eb), argent (#c0c8e0)
- **Polices** : Rajdhani (titres), Exo 2 (corps), Share Tech Mono (code/badges)
- **Framework CSS** : Bootstrap 5.3 + styles personnalisés
- **Icons** : Bootstrap Icons 1.11

---

## 🔧 Admin Django

Accès : `/admin/` (avec compte superuser)

Personnalisations :
- **Users** : gestion rôles journaliste/admin
- **Articles** : approbation, verdict, catégories
- **FactCheckResult** : historique des vérifications IA
- **Categories** : gestion des catégories d'articles

---

## 📝 Créer des catégories initiales

```python
# Dans le shell Django : python manage.py shell
from news.models import Category
categories = [
    ('Politique', 'politique', 'bi-building'),
    ('Économie', 'economie', 'bi-graph-up'),
    ('Technologie', 'technologie', 'bi-cpu'),
    ('Santé', 'sante', 'bi-heart-pulse'),
    ('Sport', 'sport', 'bi-trophy'),
    ('International', 'international', 'bi-globe'),
    ('Société', 'societe', 'bi-people'),
]
for name, slug, icon in categories:
    Category.objects.get_or_create(name=name, slug=slug, defaults={'icon': icon})
print("Catégories créées !")
```

---

## 🛡️ Sécurité (production)

Avant le déploiement en production :

```python
# settings.py
DEBUG = False
SECRET_KEY = 'votre-cle-secrete-forte'
ALLOWED_HOSTS = ['votre-domaine.dz']
```

---

*VeriDz — Combattre la désinformation en Algérie 🇩🇿*
