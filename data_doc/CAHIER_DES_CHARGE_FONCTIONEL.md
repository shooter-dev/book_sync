# CAHIER DES CHARGES FONCTIONNEL - BOOK SYNC

## 1. CONTEXTE ET OBJECTIFS

### 1.1 Présentation du projet
Book Sync est une application web de gestion de collection de livres développée dans le cadre de la formation Simplon. L'application permet aux utilisateurs de gérer leur collection personnelle de volumes, suivre leur progression de lecture et bénéficier de fonctionnalités premium avancées.

### 1.2 Objectifs métiers
- Permettre la gestion complète d'une collection de livres personnalisée
- Offrir un suivi de progression de lecture pour les utilisateurs
- Proposer des fonctionnalités premium avec statistiques avancées
- Faciliter la découverte de nouveaux contenus par genre et auteur

### 1.3 Public cible
- **Utilisateurs basiques** : Lecteurs souhaitant organiser leur collection personnelle
- **Utilisateurs premium** : Lecteurs avancés désirant des statistiques détaillées et une gestion avancée

## 2. PÉRIMÈTRE FONCTIONNEL

### 2.1 Gestion des utilisateurs
#### 2.1.1 Authentification
- Création de compte utilisateur avec email et mot de passe
- Connexion/déconnexion sécurisée
- Gestion des profils utilisateur avec pseudo unique

#### 2.1.2 Système de rôles
- **Utilisateur basique** : Accès aux fonctionnalités :
    - gestion de sa collection de livres
    - fonctionnalités premium pour une durée limitée
- **Utilisateur premium** : Accès aux fonctionnalités :
    - aux fonctionnalités basic
    - un suivi de ces lectures en cour
    - une recomendation personalisée de ces prochains lectures
    - statistiques de sa collection de livre

### 2.2 Gestion des collections
#### 2.2.1 Collection personnelle
- **Ajout de volumes** : Ajout individuel ou en groupe de volumes à la collection
- **Suppression de volumes** : Retrait individuel ou en groupe de la collection
- **Visualisation** : Affichage complet de la collection personnelle
- **Progression** : Suivi des tomes complétés dans la collection

#### 2.2.2 Métadonnées des volumes
- Titre, numéro de tome, date de sortie
- ISBN unique pour identification
- Image de couverture
- Association aux séries, genres, auteurs et éditeurs

### 2.3 Fonctionnalités premium

#### 2.3.1 Pile à lire
- Gestion d'une liste de lecture personnalisée
- Ajout/suppression de volumes lus
- Progression de lecture par rapport à la collection totale

#### 2.3.2 Statistiques avancées
- **Statistiques par genre** : Répartition de la collection
- **Historique d'ajouts** : Volumes ajoutés par mois/année
- **Historique de lecture** : Volumes lus par mois/année

### 2.4 Catalogue et métadonnées

#### 2.4.1 Organisation du contenu
- **Séries** : Regroupement logique des volumes
- **Genres** : Classification thématique avec préférences utilisateur
- **Types (Kinds)** : Catégorisation par format/support
- **Auteurs** : Gestion des créateurs avec rôles spécifiques
- **Éditeurs** : Information sur les maisons d'édition

#### 2.4.2 Système de préférences
- Gestion des genres favoris par utilisateur
- Gestion des genres non appréciés
- Gestion des types de contenu préférés

## 3. EXIGENCES TECHNIQUES

### 3.1 Architecture système
- **Framework** : Django (Python)
- **Base de données** : SQLite (développement), extensible PostgreSQL (production)
- **Frontend** : Templates Django avec CSS/HTML
- **Authentification** : Système Django natif

### 3.2 Modèle de données
#### 3.2.1 Entités principales
- **Users** : Gestion des comptes utilisateur
- **Volumes** : Références des livres avec métadonnées
- **Series** : Organisation par séries
- **Possessions** : Association utilisateur-volume
- **Authors/Jobs/Tasks** : Gestion des créateurs

#### 3.2.2 Contraintes techniques
- UUID comme clés primaires pour les entités métier
- Relations many-to-many pour les associations complexes
- Gestion des timestamps de création/modification
- Support du contenu adulte avec flag booléen

### 3.3 Performances et scalabilité
- Compteurs dénormalisés (possessions_count, tasks_count)
- Index sur les clés étrangères et champs de recherche
- Optimisation des requêtes pour les statistiques

## 4. EXIGENCES NON FONCTIONNELLES

### 4.1 Ergonomie et UX
- Interface responsive compatible mobile/desktop
- Design cohérent suivant la charte MangaCollec
- Navigation intuitive avec feedback utilisateur
- Temps de réponse < 2 secondes pour les opérations courantes

### 4.2 Sécurité
- Authentification sécurisée avec hashage des mots de passe
- Protection CSRF sur les formulaires
- Validation des données d'entrée
- Gestion des sessions sécurisée

### 4.3 Fiabilité
- Gestion des erreurs avec messages utilisateur appropriés
- Sauvegarde des données critiques
- Tests unitaires sur les fonctionnalités clés

## 5. CONTRAINTES PROJET

### 5.1 Contraintes techniques
- Développement en Django/Python
- Déploiement sur environnement Linux
- Compatible navigateurs modernes (Chrome, Firefox, Safari, Edge)

### 5.2 Contraintes réglementaires
- Conformité RGPD pour les données personnelles
- Gestion appropriée du contenu adulte
- Respect des droits d'auteur pour les métadonnées

### 5.3 Contraintes de délai
- **Développement intensif** : 4 sprints de 1 semaine (4 semaines total)
- **Sprint 1** : Foundation et authentification
- **Sprint 2** : MVP Collection Management
- **Sprint 3** : Fonctionnalités Premium 
- **Sprint 4** : IA/Prédiction et finition
- **Livraisons incrémentales** : Démonstrations hebdomadaires
- **Tests et validation continue** : Intégration quotidienne

## 6. CRITÈRES D'ACCEPTATION

### 6.1 Fonctionnalités de base (User basique)
- ✅ Création de compte et authentification
- ✅ Ajout/suppression de volumes en collection
- ✅ Visualisation de la collection personnelle
- ✅ Suivi de progression des tomes

### 6.2 Fonctionnalités premium
- ✅ Système d'abonnement premium
- ✅ Gestion de la pile à lire
- ✅ Statistiques par genre
- ✅ Historique d'activité (ajouts/lectures)

### 6.3 Qualité système
- Interface responsive sur mobile et desktop
- Temps de chargement < 2s pour les pages principales
- Aucune perte de données lors des opérations CRUD
- Sécurité des comptes utilisateur

## 7. PÉRIMÈTRE EXCLU

### 7.1 Fonctionnalités non implémentées
- Système de notation/avis sur les volumes
- Chat/messagerie entre utilisateurs
- Import/export de données
- API publique REST
- Notifications push

### 7.2 Intégrations externes
- Pas d'intégration avec des API de libraires
- Pas de synchronisation avec d'autres plateformes
- Pas de paiement en ligne pour l'abonnement premium

## 8. ANNEXES

### 8.1 Références techniques
- Modèle UML : `data_doc/annexe/uml/mcd_bdd/mcd_bdd.plantuml`
- User stories : `data_doc/agile/user_story.md`
- Configuration Django : `book_sync/core/settings.py`

### 8.2 Environnement de développement
- Python 3.12+
- Django 5.x
- Dépendances listées dans `requirements.txt`

---

**Version** : 1.0  
**Date** : 8/08/2025  
**Projet** : Book Sync - Formation Simplon  
**Équipe** : Développeurs Simplon (
[sayana-project](https://github.com/sayana-project),
[elvis-messiaen](https://github.com/elvis-messiaen),
[shooter-dev](https://github.com/shooter-dev))