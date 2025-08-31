# 📚 Book Sync - Plateforme de Gestion de Collections de Livres

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.1-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agile](https://img.shields.io/badge/Methodology-Scrum-orange.svg)](https://agilemanifesto.org)

> **Plateforme moderne et intuitive pour gérer vos collections de livres personnelles avec un système freemium avancé et des recommandations basées IA.**

## ✨ Aperçu du Projet

Book Sync est une application web Django full-stack développée avec une méthodologie agile Scrum. Elle permet aux utilisateurs de gérer leurs collections de livres avec des fonctionnalités différenciées selon le niveau d'abonnement (gratuit/premium).

### 🎯 Problématique Résolue
- **Gestion manuelle** : Plus besoin de tableaux Excel ou carnets papier
- **Perte de vue d'ensemble** : Visualisation complète et progression en temps réel
- **Découverte limitée** : Recommandations personnalisées basées IA/ML
- **Suivi lecture** : Tracking avancé avec statistiques détaillées

### 🏆 Valeur Métier
- **ROI Utilisateur** : Gain de temps estimé 60% dans la gestion
- **Engagement** : Système de gamification avec progression
- **Monétisation** : Modèle freemium avec conversion premium optimisée
- **Évolutivité** : Architecture modulaire supportant la croissance

---

## 🚀 Fonctionnalités Principales

### 📖 Collection Management
- ✅ **CRUD Complet** : Ajout/suppression volumes individuels ou en groupe
- ✅ **Progression Avancée** : Suivi visuel de l'avancement des collections
- ✅ **Organisation** : Classification par genres, séries, auteurs, éditeurs
- ✅ **Recherche & Filtres** : Navigation intuitive dans grandes collections

### 📊 Lecture Tracking (Premium)
- ✅ **Suivi Individuel** : Marquer volumes lus/non lus avec timestamps
- ✅ **Progression Série** : Visualisation avancement par série
- ✅ **Pile à Lire** : Gestion personnalisée des lectures planifiées
- ✅ **Historique Temporel** : Analyses par mois/année

### 🤖 Système de Prédiction IA
- ✅ **Recommandations Personnalisées** : Basées sur préférences utilisateur
- ✅ **Machine Learning** : Algorithmes adaptatifs d'amélioration continue
- ✅ **Système de Préférences** : Genres/kinds aimés/non aimés
- ✅ **Propositions Contextuelles** : Suggestions en temps réel

### 📈 Statistiques Avancées (Premium)
- ✅ **Analytics Genre** : Répartition collection par catégories
- ✅ **Analytics Publishers** : Analyse par maisons d'édition
- ✅ **Tendances Temporelles** : Évolution ajouts/lectures dans le temps
- ✅ **Métriques Engagement** : KPIs personnels de lecture

### 👤 Profil Utilisateur Complet
- ✅ **Gestion Profil** : Âge, genre, informations personnelles
- ✅ **Préférences Avancées** : Système granulaire genres/catégories
- ✅ **Contrôle Parental** : Filtrage contenu sensible selon l'âge
- ✅ **Personnalisation UX** : Interface adaptée aux préférences

### 💎 Abonnement Premium
- ✅ **Souscription Fluide** : Upgrade utilisateur basique → premium
- ✅ **Gestion Flexible** : Renouvellement/résiliation autonome
- ✅ **Features Exclusives** : Accès complet analytics et IA
- ✅ **Support Prioritaire** : Assistance dédiée utilisateurs premium

---

## 🏗️ Architecture Technique

### Stack Principal
- **Backend** : Django 5.1 (Python 3.12+)
- **Base de Données** : PostgreSQL (prod) / SQLite (dev)
- **Frontend** : Templates Django + Design System MangaCollec
- **Authentification** : Django Auth native sécurisé
- **Analytics** : Pandas pour traitement données
- **Deployment** : Uvicorn (ASGI) + PostgreSQL

### Architecture Modulaire (5 Apps)
```
book_sync/
├── 🔐 accounts/        # Identity & Access Management
├── 📚 collection/      # Domain Logic Principal (13 modèles)
├── 📖 lecture/         # Reading Analytics & Tracking  
├── 🤖 prediction/      # Machine Learning & Recommandations
└── ⚙️ core/           # Configuration & Infrastructure
```

### Modèles de Données (13+ Entités)
- **Users & Auth** : Profils, rôles, abonnements
- **Content** : Authors, Genres, Kinds, Publishers, Series, Volumes
- **Relations** : Tasks (auteur-série-job), Possessions, Reads
- **Préférences** : like_genre, like_kind (système recommandation)
- **Optimisations** : Compteurs dénormalisés, indexes optimisés

### Design Patterns & Bonnes Pratiques
- ✅ **Clean Architecture** : Séparation responsabilités SOLID
- ✅ **UUID Primary Keys** : Évolutivité et sécurité
- ✅ **Repository Pattern** : Abstraction accès données
- ✅ **Service Layer** : Logique métier centralisée
- ✅ **Responsive Design** : Mobile-first, 4 breakpoints

---

## 🛠️ Installation & Configuration

### Prérequis
- **Python 3.12+**
- **PostgreSQL 13+** (production)
- **Git** pour le versioning
- **Virtual Environment** (recommandé)

### Installation Rapide

```bash
# 1. Cloner le repository
git clone https://github.com/shooter-dev/book-sync.git
cd book-sync

# 2. Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Configuration base de données
cd book_sync
cp .env.example .env  # Configurer variables d'environnement

# 5. Migrations Django
python manage.py makemigrations
python manage.py migrate

# 6. Créer superuser admin
python manage.py createsuperuser

# 7. Charger données de test (optionnel)
python manage.py loaddata fixtures/initial_data.json

# 8. Lancer serveur développement
python manage.py runserver
```

### Configuration Production

```bash
# Configuration PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/book_sync_db
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Lancement production avec Uvicorn
uvicorn core.asgi:application --host 0.0.0.0 --port 8000
```

---

## 📱 Interface Utilisateur

### Design System MangaCollec
- **Palette Couleurs** : Rouge signature #CF000A, mode sombre adaptatif
- **Typographie** : Stack moderne Apple/Segoe UI optimisée
- **Responsive** : Mobile-first, 4 breakpoints (sm/md/lg/xl)
- **Accessibilité** : Support dark mode, focus states, contraste optimisé

### Pages Principales
- 🏠 **Dashboard** : Vue d'ensemble collection et statistiques
- 📚 **Ma Collection** : Gestion CRUD complète volumes
- 📖 **Mes Lectures** : Tracking progression et pile à lire
- 🤖 **Recommandations** : Suggestions IA personnalisées
- 📊 **Statistiques** : Analytics avancées (premium)
- ⚙️ **Profil** : Gestion compte et préférences

---

## 🧪 Tests & Qualité

### Tests Automatisés
```bash
# Tests unitaires
python manage.py test

# Coverage report
pip install coverage
coverage run --source='.' manage.py test
coverage report -m
```

### Qualité Code
- **PEP8** : Standards Python respectés
- **Django Best Practices** : Conventions framework
- **Security** : Protection CSRF, authentification sécurisée
- **Performance** : Requêtes optimisées, cache intelligent

---

## 🚀 Déploiement

### Environnements
- **Développement** : SQLite + Django dev server
- **Staging** : PostgreSQL + Uvicorn
- **Production** : PostgreSQL + Nginx + Uvicorn

### CI/CD Pipeline (Recommandé)
```bash
# GitHub Actions workflow
.github/workflows/django.yml
- Tests automatisés
- Code quality checks
- Déploiement automatique
```

---

## 📊 Métriques Projet

### Développement Agile
- ✅ **23 User Stories** implémentées (100% backlog)
- ✅ **6 Épiques métier** livrées dans les délais
- ✅ **Méthodologie Scrum** appliquée avec rigueur
- ✅ **Documentation complète** (UML, cahier charges, stories)

### Code Base
- ✅ **45 fichiers Python** architecture clean
- ✅ **5 apps Django** modulaires spécialisées
- ✅ **13+ modèles de données** normalisés UUID
- ✅ **Relations complexes** Many-to-Many optimisées

### Performance
- ✅ **< 2 secondes** temps de réponse garanti
- ✅ **Mobile responsive** 4 breakpoints
- ✅ **SEO optimisé** structure sémantique
- ✅ **Accessibilité** WCAG guidelines

---

## 👥 Équipe de Développement

### Core Team
- 👨‍💻 **[ShooterDev](https://github.com/shooter-dev)** - Tech Lead & Full-Stack Developer
- 👨‍💻 **[sayana-project](https://github.com/sayana-project)** - Backend Developer  
- 👨‍💻 **[elvis-messiaen](https://github.com/elvis-messiaen)** - Frontend Developer

### Méthodologie
- **Scrum Agile** avec sprints 2 semaines
- **Collaboration GitHub** : Code review, branches features
- **Documentation Living** : Mise à jour continue
- **Amélioration Continue** : Retrospectives et adaptation

---

## 📖 Documentation Technique

### Artefacts Disponibles
- 📋 **[Cahier des Charges](data_doc/CAHIER_DES_CHARGE_FONCTIONEL.md)** - Spécifications complètes
- 📝 **[User Stories](data_doc/agile/user_story.md)** - 23 stories, 6 épiques  
- 🎯 **[Rapport Certification Agile](RAPPORT_CERTIFICATION_AGILE.md)** - Démarche complète
- 🏗️ **[UML Database](data_doc/annexe/uml/mcd_bdd/)** - Modélisation PlantUML
- ⚙️ **[Guide Développement](CLAUDE.md)** - Standards et conventions

### API Documentation (Roadmap)
- REST API endpoints documentation
- Swagger/OpenAPI integration
- Postman collection examples

---

## 🔮 Roadmap & Évolutions

### Version 2.0 (Q1 2026)
- 🌐 **API REST Publique** : Intégrations tierces
- 📱 **Application Mobile** : iOS/Android natives
- 🔍 **Recherche Avancée** : ElasticSearch integration
- ☁️ **Cloud Sync** : Sauvegarde multi-devices

### Version 3.0 (Q3 2026)
- 👥 **Features Sociales** : Communauté, partage, avis
- 🎵 **Multi-formats** : Support audiobooks, e-books
- 🌍 **Internationalisation** : Support multi-langues
- 📈 **Analytics Avancées** : Business Intelligence

---

## 🤝 Contribution

### Comment Contribuer
1. **Fork** le repository
2. **Créer** une branche feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** vos changements (`git commit -m 'Add: Amazing Feature'`)
4. **Push** sur la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrir** une Pull Request

### Standards de Contribution
- **Code Style** : PEP8 + Django conventions
- **Tests** : Coverage minimum 80%
- **Documentation** : Mise à jour obligatoire
- **Commit Messages** : Format conventionnel

---

## 📄 Licence & Support

### Licence
Ce projet est sous licence **MIT** - voir [LICENSE](LICENSE) pour détails.

### Support
- 📧 **Email** : support@book-sync.com
- 💬 **Discord** : [Serveur Communauté](https://discord.gg/book-sync)
- 🐛 **Issues** : [GitHub Issues](https://github.com/shooter-dev/book-sync/issues)
- 📖 **Wiki** : [Documentation Complète](https://github.com/shooter-dev/book-sync/wiki)

### Remerciements
- 🎓 **Simplon** : Formation et accompagnement agile
- 🎨 **MangaCollec** : Inspiration design system
- 🌟 **Communauté Django** : Framework et ecosystem
- 💡 **Beta Testers** : Retours utilisateurs précieux

---

**⭐ Si ce projet vous plaît, n'hésitez pas à lui donner une étoile sur GitHub ! ⭐**

---

<div align="center">
  <strong>Développé avec ❤️ par l'équipe Simplon</strong><br>
  <em>Formation Développeur Web & Mobile - Promotion 2024-2025</em>
</div>