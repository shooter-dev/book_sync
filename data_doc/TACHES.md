# Tâches de Développement - BookSync

## Épic 1 : Collection

### T001V - Affichage de la collection (Vue)
- **US associée** : S001 - Voir ma collection de volumes
- **Description** : Interface utilisateur pour afficher la collection avec infinite scroll
- **Critères d'acceptation** :
  - Interface responsive avec cards Tailwind CSS
  - Chargement automatique au scroll (infinite scroll)
  - Filtres visuels par série, genre et auteur
- **Estimation** : 3 points
- **Priorité** : Haute
- **📋 Résumé technique** :
  1. **Template responsive** : Créer un template HTML avec des cards Tailwind CSS pour afficher chaque volume
  2. **Loading indicator** : Afficher un indicateur de chargement pendant le fetch des données
  3. **Filtres UI** : Interface de filtres par série, genre et auteur avec dropdowns
  4. **Scroll detection** : JavaScript pour détecter quand l'utilisateur approche du bas de page
  5. **States management** : Gérer les états de chargement, vide, erreur
  6. **Responsive design** : Adaptation mobile avec grille flexible

### T001L - Affichage de la collection (Logique)
- **US associée** : S001 - Voir ma collection de volumes
- **Description** : API et logique pour le chargement de la collection avec pagination
- **Critères d'acceptation** :
  - API endpoint pour infinite scroll
  - Requête optimisée avec relations
  - Filtrage et tri des données
- **Estimation** : 4 points
- **Priorité** : Haute
- **📋 Résumé technique** :
  1. **API endpoint** : Créer `/api/collection/` pour récupérer les possessions paginées
  2. **Requête optimisée** : Utiliser select_related et prefetch_related pour charger possessions, volumes et séries
  3. **Pagination** : Implémenter pagination par offset/limit pour infinite scroll
  4. **Filtrage** : Logique de filtrage par série, genre et auteur
  5. **Authentification** : S'assurer que seuls les utilisateurs connectés accèdent à leur collection
  6. **Serialization** : Sérialiser les données pour l'API JSON

### T002L - Logique d'ajout de volume (Métier)
- **US associée** : S002 - Ajouter un volume à ma collection
- **Description** : API et validation pour l'ajout d'un volume à la collection
- **Critères d'acceptation** :
  - API unifiée pour ajout depuis différents contextes
  - Validation et sécurité des opérations
  - Gestion des erreurs et doublons
- **Estimation** : 3 points
- **Priorité** : Haute
- **Dépendances** : T017L (Modèles Django) + T013V (Pages détail série/volume)
- **📋 Résumé technique** :
  1. **API ajout simple** : `/api/collection/add-volumes/`
  2. **API ajout multiple** : `/api/collection/add-volumes/`
  3. **Validation métier** : Vérifier utilisateur connecté, volume existant, pas déjà possédé
  4. **Création possession** : Instancier Possession(user, volume, created_at)
  5. **Transactions atomiques** : Garantir la cohérence des données
  6. **Gestion d'erreurs** : Codes HTTP explicites (`409` si déjà possédé, `401` si non connecté)
  7. **Logging** : Tracer les ajouts pour audit et statistiques
  8. **Sécurité** : Protection CSRF et validation des permissions

### T003V - Interface d'ajout multiple (Vue)
- **US associée** : S003 - Rajouter plusieurs volumes du même série à ma collection
- **Description** : Pop-up modale avec liste déroulante pour ajout multiple de volumes
- **Critères d'acceptation** :
  - Bouton "Ajouter plusieurs volumes" sur page série
  - Pop-up modale avec liste déroulante des volumes non possédés
  - Sélection multiple avec validation et confirmation
- **Estimation** : 2 points
- **Priorité** : Moyenne
- **Dépendances** : T013V (Page détail série)
- **📋 Résumé technique** :
  1. **Bouton trigger** : "Ajouter plusieurs volumes" sur page série
  2. **Pop-up modale** : Modal Tailwind CSS responsive et accessible
  3. **Liste déroulante** : Select multiple avec volumes non possédés de la série
  4. **Interface sélection** : Checkboxes ou multi-select avec recherche
  5. **Validation** : Boutons "Annuler" et "Ajouter X volumes sélectionnés"
  6. **Feedback** : Loading state et confirmation après ajout

### T003L - Logique d'ajout multiple (Métier)
- **US associée** : S003 - Rajouter plusieurs volumes du même série à ma collection
- **Description** : API et traitement pour l'ajout en lot de volumes d'une série
- **Critères d'acceptation** :
  - API batch pour ajout multiple efficace
  - Validation que volumes appartiennent à la même série
  - Gestion des erreurs partielles
- **Estimation** : 4 points
- **Priorité** : Moyenne
- **Dépendances** : T002L (Logique ajout simple)
- **📋 Résumé technique** :
  1. **API batch** : Utilise `/api/collection/add-volume/` (même endpoint que T002L) pour ajout en lot
  2. **Validation série** : Vérifier que tous les volume_ids appartiennent à la série
  3. **Bulk operations** : Utiliser Django bulk_create pour performance
  4. **Transactions atomiques** : Garantir cohérence (tout ou rien)
  5. **Gestion erreurs partielles** : Rapporter les échecs individuels
  6. **Statistiques** : Mettre à jour les compteurs de progression série
  7. **Logging détaillé** : Tracer les ajouts en lot pour audit

### T004L - Logique de suppression (Métier)
- **US associée** : S004/S005 - Retirer un/plusieurs volumes de ma collection
- **Description** : API pour suppression sécurisée simple et multiple
- **Critères d'acceptation** :
  - APIs suppression avec validation des permissions
  - Suppression en lot optimisée
  - Audit trail des suppressions
- **Estimation** : 3 points
- **Priorité** : Moyenne
- **📋 Résumé technique** :
  1. **API suppression simple** : `/api/collection/delete-volumes/`
  2. **API suppression multiple** : `/api/collection/delete-volumes/`
  3. **Validation sécurité** : Vérifier que possessions appartiennent à l'utilisateur
  4. **Bulk delete** : Opération optimisée pour suppression multiple
  5. **Soft delete optionnel** : Marquer comme supprimé au lieu d'effacer
  6. **Logging audit** : Tracer toutes les suppressions

### T005V - Interface remove multiple (Vue)
- **US associée** : S005 - Retirer plusieurs volumes de ma collection
- **Description** : Pop-up modale avec liste déroulante pour suppression multiple de volumes
- **Critères d'acceptation** :
  - Bouton "Supprimer plusieurs volumes" sur page collection
  - Pop-up modale avec liste déroulante des volumes possédés
  - Sélection multiple avec validation et confirmation
- **Estimation** : 2 points
- **Priorité** : Moyenne
- **Dépendances** : T001V (Interface collection)
- **📋 Résumé technique** :
  1. **Bouton trigger** : "Supprimer plusieurs volumes" sur page collection
  2. **Pop-up modale** : Modal Tailwind CSS responsive et accessible
  3. **Liste déroulante** : Select multiple avec volumes possédés de l'utilisateur
  4. **Interface sélection** : Checkboxes ou multi-select avec recherche
  5. **Validation** : Boutons "Annuler" et "Supprimer X volumes sélectionnés"
  6. **Feedback** : Loading state et confirmation après suppression

### T006V - Interface progression collection (Vue)
- **US associée** : S006/S007 - Voir la progression de ma collection
- **Description** : Page progression avec widget global en haut et liste détaillée par série
- **Critères d'acceptation** :
  - Widget progression globale en haut de page
  - Liste volumes par série avec infos détaillées
  - Barres de progression par série avec pourcentages
- **Estimation** : 4 points
- **Priorité** : Moyenne
- **📋 Résumé technique** :
  1. **Widget progression globale** : Card en haut avec progression totale de la collection
  2. **Liste par série** : Cards triées par série avec cover et informations
  3. **Infos série** : Titre, nombre possédé/total, volumes manquants
  4. **Barres progression** : Barre CSS par série avec pourcentage de complétion
  5. **Tri et filtres** : Tri par nom, progression, ou nombre de volumes
  6. **Design responsive** : Layout adaptatif avec grille flexible

### T006L - Logique progression collection (Métier)
- **US associée** : S006/S007 - Voir la progression de ma collection
- **Description** : Calculs et API pour statistiques de progression par série
- **Critères d'acceptation** :
  - API pour données de progression optimisée
  - Calculs de pourcentages de complétion
  - Statistiques globales utilisateur
- **Estimation** : 4 points
- **Priorité** : Moyenne
- **📋 Résumé technique** :
  1. **API progression** : `/api/collection/progress/` avec calculs optimisés
  2. **Requêtes annotations** : Utiliser Django ORM annotations pour calculs
  3. **Calculs pourcentages** : (volumes possédés / volumes totaux) * 100
  4. **Cache statistiques** : Redis cache pour performances
  5. **Aggregations** : Count, Sum pour statistiques globales
  6. **Optimization** : Index sur champs de calcul fréquents

## Épic 2 : Lecture (Premium)

### T007V - Interface lecture Premium (Vue)
- **US associée** : S008/S009 - Marquer volumes comme lus
- **Description** : Interfaces pour marquage lecture simple et multiple (Premium)
- **Critères d'acceptation** :
  - Boutons "Marquer comme lu" avec états visuels
  - Mode sélection multiple pour marquage en lot
  - Indicateurs visuels lecture (vert=lu, bleu=possédé)
- **Estimation** : 4 points
- **Priorité** : Moyenne
- **Restriction** : Premium uniquement
- **📋 Résumé technique** :
  1. **Boutons lecture** : "Marquer comme lu" sur volumes possédés
  2. **États visuels** : Codes couleurs (vert=lu, bleu=possédé, gris=manquant)
  3. **Sélection multiple** : Interface similaire à ajout multiple
  4. **Progress tracking** : Barres de progression lecture par série
  5. **Premium gate** : Masquer fonctionnalités si pas Premium
  6. **Feedback spécialisé** : Messages spécifiques à la lecture

### T007L - Logique lecture Premium (Métier)
- **US associée** : S008/S009 - Marquer volumes comme lus
- **Description** : API pour tracking de lecture avec validation Premium
- **Critères d'acceptation** :
  - API marquage lecture avec vérification Premium
  - Calculs progression lecture par série
  - Statistiques temporelles de lecture
- **Estimation** : 5 points
- **Priorité** : Moyenne
- **Restriction** : Premium uniquement
- **📋 Résumé technique** :
  1. **Validation Premium** : Middleware vérification abonnement actif
  2. **API marquage** : `/api/volumes/{id}/read/` avec horodatage
  3. **Modèle Read** : Création enregistrement Read(user, volume, created_at)
  4. **Bulk marking** : API pour marquage multiple efficace
  5. **Statistics** : Calculs rythme lecture, volumes/mois
  6. **Downgrade handling** : Gestion perte Premium (données conservées)

### T008V - Interface progression lecture (Vue)
- **US associée** : S010 - Voir la progression de ma lecture par série
- **Description** : Visualisation avancement lecture avec doubles barres
- **Critères d'acceptation** :
  - Barres doubles CSS (possession vs lecture)
  - Icônes pour distinction des états de lecture
  - Progression temporelle par série
- **Estimation** : 4 points
- **Priorité** : Moyenne
- **📋 Résumé technique** :
  1. **Barres doubles** : Barres CSS superposées - possession + lecture par série
  2. **Système d'icônes** : 📖 = lu, 📚 = possédé non lu, ❌ = manquant
  3. **Liste chronologique** : Affichage simple par mois/année des volumes lus
  4. **Filtres avancés** : Par genre, période, statut lecture
  5. **Recommandations** : Suggestions prochains volumes à lire
  6. **Légende icônes** : Affichage explicite du système d'icônes

### T008L - Logique progression lecture (Métier)
- **US associée** : S010 - Voir la progression de ma lecture par série
- **Description** : Calculs complexes progression lecture avec historique
- **Critères d'acceptation** :
  - Calculs progression lecture par série
  - Statistiques temporelles (mois/année)
  - Recommandations basées progression
- **Estimation** : 5 points
- **Priorité** : Moyenne
- **📋 Résumé technique** :
  1. **Calculs complexes** : Progression possession vs lecture par série
  2. **Queries temporelles** : GROUP BY mois/année pour historiques
  3. **API recommandations** : Suggérer prochains volumes selon progression
  4. **Performance** : Cache calculs coûteux avec invalidation
  5. **Analytics** : Métriques rythme lecture, temps moyen par volume
  6. **Data aggregation** : Pré-calcul statistiques pour dashboard

## Épic 3 : Prédiction

### T009V - Interface recommandations (Vue)
- **US associée** : S011 - Proposition de prochaine lecture
- **Description** : Page recommandations avec cards attractives et explications
- **Critères d'acceptation** :
  - Cards recommandations avec covers et descriptions
  - Explications des choix ("Car vous aimez X")
  - Actions rapides (ajout direct, pas intéressé)
- **Estimation** : 5 points
- **Priorité** : Basse
- **📋 Résumé technique** :
  1. **Cards recommandations** : Design attractif avec cover, titre, raison
  2. **Explications** : "Recommandé car vous aimez [Genre]" ou "Fans de [Auteur]"
  3. **Actions rapides** : Boutons "Ajouter", "Pas intéressé", "Détails"
  4. **Feedback système** : Pouces haut/bas pour améliorer algorithme
  5. **Actualisation** : Bouton "Nouvelles recommandations"
  6. **États vides** : Gestion cas pas assez de données

### T009L - Logique recommandations IA (Métier)
- **US associée** : S011 - Proposition de prochaine lecture
- **Description** : Algorithme de recommandation basé préférences et historique
- **Critères d'acceptation** :
  - Algorithme scoring basé préférences utilisateur
  - Filtrage collaboratif simple
  - Exclusion volumes déjà possédés
- **Estimation** : 10 points
- **Priorité** : Basse
- **📋 Résumé technique** :
  1. **Analyse préférences** : Genres/kinds aimés vs historique lecture/possession
  2. **Scoring algorithm** : Système de points basé préférences + popularité
  3. **Collaborative filtering** : "Utilisateurs similaires ont aussi aimé"
  4. **Exclusions** : Filtrer volumes déjà possédés/lus
  5. **Diversification** : Mix préférences + découverte nouveaux genres
  6. **Machine learning** : Collecte feedback pour amélioration continue
  7. **Performance** : Cache recommandations, recalcul périodique

## Épic 4 : Statistiques (Premium)

### T010V - Interface statistiques Premium (Vue)
- **US associée** : S012/S013/S014/S015 - Statistiques de collection avancées
- **Description** : Dashboards statistiques avec graphiques interactifs (Premium)
- **Critères d'acceptation** :
  - Graphiques par genre et éditeur
  - Historiques d'ajout mensuels/annuels
  - Interface responsive et interactive
- **Estimation** : 6 points
- **Priorité** : Basse
- **Restriction** : Premium uniquement
- **📋 Résumé technique** :
  1. **Dashboard principal** : Vue d'ensemble avec KPIs principaux
  2. **Graphiques genre** : Camembert + barres Chart.js interactifs
  3. **Graphiques éditeur** : Top éditeurs avec drill-down
  4. **Calendrier activité** : Heatmap style GitHub des ajouts
  5. **Export données** : PDF/CSV des statistiques
  6. **Comparaisons** : Évolution par rapport mois/année précédents

### T010L - Logique statistiques Premium (Métier)
- **US associée** : S012/S013/S014/S015 - Statistiques de collection avancées
- **Description** : APIs calculs statistiques complexes avec optimisations
- **Critères d'acceptation** :
  - APIs agrégation par genre, éditeur, période
  - Calculs historiques optimisés
  - Cache pour performances
- **Estimation** : 6 points
- **Priorité** : Basse
- **Restriction** : Premium uniquement
- **📋 Résumé technique** :
  1. **APIs statistiques** : Endpoints spécialisés par type statistique
  2. **Aggregations complexes** : Django ORM avec annotations avancées
  3. **Calculs temporels** : TruncMonth/TruncYear pour historiques
  4. **Cache système** : Redis pour statistiques coûteuses
  5. **Batch processing** : Pré-calcul statistiques globales
  6. **Performance monitoring** : Métriques temps calcul statistiques

## Épic 5 : Profil

### T011V - Interface profil utilisateur (Vue)
- **US associée** : S023/S024/S025/S026/S027 - Gestion profil et préférences
- **Description** : Pages paramètres profil avec formulaires interactifs
- **Critères d'acceptation** :
  - Formulaires profil (âge, genre, préférences)
  - Interface préférences genres/kinds avec étoiles
  - Paramètres contenu sensible avec explications
- **Estimation** : 4 points
- **Priorité** : Moyenne
- **📋 Résumé technique** :
  1. **Formulaires profil** : Âge (slider), genre (radio buttons), informations
  2. **Préférences interactives** : Cards genres/kinds avec rating étoiles
  3. **Sauvegarde AJAX** : Sauvegarde automatique sans rechargement
  4. **Validation temps réel** : Feedback immédiat sur saisies
  5. **Paramètres contenu** : Toggle avec explications âge légal
  6. **Navigation onglets** : Organisation par catégories de paramètres

### T011L - Logique profil utilisateur (Métier)
- **US associée** : S023/S024/S025/S026/S027 - Gestion profil et préférences
- **Description** : APIs sécurisées pour modification profil et préférences
- **Critères d'acceptation** :
  - APIs modification profil avec validation
  - Gestion préférences genres/kinds
  - Validation contenu sensible selon âge
- **Estimation** : 5 points
- **Priorité** : Moyenne
- **📋 Résumé technique** :
  1. **API profil** : `/api/profile/` PATCH pour modifications partielles
  2. **Validation métier** : Âge 10-99, genre énumération, contenu selon âge
  3. **Préférences relations** : Models UserGenrePreference, UserKindPreference
  4. **Sécurité** : Validation permissions, CSRF protection
  5. **Audit changes** : Log modifications profil pour sécurité
  6. **Impact recommandations** : Trigger recalcul recommandations

## Épic 6 : Recherche

### T012V - Interface de recherche (Vue)
- **US associée** : S016/S017/S018 - Rechercher série/publisher/auteur
- **Description** : Interface de recherche unifiée avec autocomplétion
- **Critères d'acceptation** :
  - Barre de recherche globale avec suggestions
  - Onglets série/publisher/auteur
  - Résultats enrichis avec actions rapides
- **Estimation** : 5 points
- **Priorité** : Haute
- **📋 Résumé technique** :
  1. **Barre recherche globale** : Input avec autocomplétion en temps réel
  2. **Suggestions dropdown** : Résultats mixed avec catégorisation
  3. **Onglets résultats** : Séparation série/publisher/auteur avec compteurs
  4. **Cards résultats** : Design uniforme avec cover, infos, actions
  5. **Filtres avancés** : Sidebar avec filtres par genre, kind, année
  6. **Historique recherches** : Sauvegarde recherches récentes

### T012L - Logique de recherche (Métier)
- **US associée** : S016/S017/S018 - Rechercher série/publisher/auteur
- **Description** : Moteur de recherche full-text avec APIs optimisées
- **Critères d'acceptation** :
  - API recherche full-text performante
  - Autocomplétion temps réel
  - Filtrage avancé et tri pertinence
- **Estimation** : 6 points
- **Priorité** : Haute
- **📋 Résumé technique** :
  1. **API recherche** : `/api/search/` avec paramètres query, type, filters
  2. **Full-text search** : Utilisation icontains Django ou PostgreSQL FTS
  3. **Autocomplétion** : Endpoint dédié limite 10 suggestions rapides
  4. **Indexation** : Index base données sur champs recherche fréquents
  5. **Ranking** : Algorithme pertinence basé popularité + correspondance
  6. **Performance** : Cache recherches fréquentes, débouncing API

### T013V - Interface pages détail (Vue)
- **US associée** : S016/S017/S018 - Voir détail série/publisher/auteur
- **Description** : Pages détaillées pour série, publisher et auteur
- **Critères d'acceptation** :
  - Page série avec grille volumes et infos complètes
  - Page publisher avec catalogue et informations
  - Page auteur avec biographie et œuvres
- **Estimation** : 6 points
- **Priorité** : Haute
- **📋 Résumé technique** :
  1. **Page série** : Header (cover, titre, infos) + grille volumes avec statuts
  2. **Page publisher** : Logo, informations, catalogue séries avec filtres
  3. **Page auteur** : Photo, biographie, liste œuvres avec rôles
  4. **Navigation** : Breadcrumb, liens contextuels, précédent/suivant
  5. **Actions utilisateur** : Boutons ajout/suppression selon contexte
  6. **SEO** : Meta tags, structured data, URLs propres

### T013L - Logique pages détail (Métier)
- **US associée** : S016/S017/S018 - Voir détail série/publisher/auteur
- **Description** : APIs pour récupération données détaillées optimisées
- **Critères d'acceptation** :
  - APIs détail avec relations optimisées
  - Calcul statuts possession/lecture
  - Données enrichies pour SEO
- **Estimation** : 4 points
- **Priorité** : Haute
- **📋 Résumé technique** :
  1. **APIs détail** : `/api/series/{id}/`, `/api/volumes/{id}/`, `/api/authors/{id}/`
  2. **Optimisation requêtes** : select_related/prefetch_related pour éviter N+1
  3. **Statuts utilisateur** : Calcul possession/lecture si connecté
  4. **Serializers complets** : Inclusion relations nécessaires frontend
  5. **Cache objets** : Redis cache pour objets consultés fréquemment
  6. **404 handling** : Gestion propre objets non trouvés

## Épic 7 : Authentification et Compte

### T014V - Interface authentification (Vue)
- **US associée** : S019 - Création compte et connexion
- **Description** : Pages d'authentification avec design MangaCollec
- **Critères d'acceptation** :
  - Formulaires inscription/connexion responsive
  - Validation temps réel et gestion erreurs
  - Design cohérent avec charte graphique
- **Estimation** : 3 points
- **Priorité** : Haute
- **📋 Résumé technique** :
  1. **Formulaires auth** : Design MangaCollec avec validation live
  2. **Messages erreurs** : Affichage clair et contextualisé
  3. **États formulaires** : Loading, disabled pendant soumission
  4. **Responsive design** : Adaptation mobile optimisée
  5. **Accessibility** : Labels, focus states, navigation clavier
  6. **Social auth UI** : Boutons OAuth si implémenté

### T014L - Logique authentification (Métier)
- **US associée** : S019 - Création compte et connexion
- **Description** : Système d'auth sécurisé avec validation email
- **Critères d'acceptation** :
  - APIs inscription/connexion sécurisées
  - Validation email obligatoire
  - Système de rôles User/Premium
- **Estimation** : 6 points
- **Priorité** : Haute
- **📋 Résumé technique** :
  1. **Django auth** : Utilisation système auth Django avec User étendu
  2. **Email validation** : Tokens confirmation avec expiration
  3. **Password security** : Validation force + hachage sécurisé
  4. **Role system** : Field role avec middleware permissions
  5. **Session management** : Configuration sessions sécurisées
  6. **Rate limiting** : Protection contre brute force
  7. **CSRF protection** : Tokens CSRF sur toutes formes auth

### T015V - Interface gestion compte (Vue)
- **US associée** : S020/S021/S022 - Gestion mot de passe, email, suppression compte
- **Description** : Interfaces pour modifications compte sensibles
- **Critères d'acceptation** :
  - Formulaires modification mot de passe et email
  - Processus suppression compte avec confirmations
  - Feedback sécurisé pour actions sensibles
- **Estimation** : 3 points
- **Priorité** : Moyenne
- **📋 Résumé technique** :
  1. **Formulaire mot de passe** : Ancien + nouveau + confirmation avec force meter
  2. **Changement email** : Process deux étapes avec confirmations
  3. **Suppression compte** : Workflow multi-étapes avec avertissements
  4. **Confirmations sécurisées** : Modals avec re-saisie mot de passe
  5. **Messages feedback** : Notifications succès/erreur appropriées
  6. **États processus** : Indicateurs étapes pour workflows longs

### T015L - Logique gestion compte (Métier)
- **US associée** : S020/S021/S022 - Gestion mot de passe, email, suppression compte
- **Description** : APIs sécurisées pour modifications compte critiques
- **Critères d'acceptation** :
  - APIs modification sécurisées avec validation
  - Processus email à deux étapes
  - Suppression compte conforme RGPD
- **Estimation** : 6 points
- **Priorité** : Moyenne
- **📋 Résumé technique** :
  1. **Change password API** : Validation ancien + force nouveau mot de passe
  2. **Change email API** : Process avec tokens validation deux emails
  3. **Delete account API** : Soft delete avec période grâce 7 jours
  4. **Data anonymization** : Anonymisation données vs suppression selon RGPD
  5. **Security audit** : Log toutes actions sensibles compte
  6. **Email notifications** : Notifications sécurité changements critiques

## Épic 8 : Abonnement Premium

### T016V - Interface abonnement Premium (Vue)
- **US associée** : S028/S029/S030 - Gestion abonnement Premium
- **Description** : Pages souscription, gestion et résiliation Premium
- **Critères d'acceptation** :
  - Page marketing Premium avec comparatif features
  - Interface souscription Stripe intégrée
  - Dashboard gestion abonnement
- **Estimation** : 5 points
- **Priorité** : Moyenne
- **📋 Résumé technique** :
  1. **Page marketing** : Comparatif User vs Premium avec call-to-action
  2. **Stripe checkout** : Intégration Stripe Elements pour paiement
  3. **Dashboard abonnement** : Statut, échéances, historique factures
  4. **Process résiliation** : Workflow guidé avec feedback collection
  5. **États visuels** : Badges Premium, countdown expiration
  6. **Responsive pricing** : Tableau prix adaptatif mobile

### T016L - Logique abonnement Premium (Métier)
- **US associée** : S028/S029/S030 - Gestion abonnement Premium
- **Description** : Intégration Stripe complète avec webhooks
- **Critères d'acceptation** :
  - Intégration Stripe pour paiements récurrents
  - Webhooks gestion événements paiement
  - Logique upgrade/downgrade automatique
- **Estimation** : 8 points
- **Priorité** : Moyenne
- **📋 Résumé technique** :
  1. **Stripe integration** : Configuration produits/prix Stripe
  2. **Subscription model** : Model tracking abonnements avec dates
  3. **Webhooks handling** : Gestion events Stripe (payment, expiry, etc.)
  4. **Role management** : Upgrade/downgrade automatique User<->Premium
  5. **Grace period** : Maintien accès quelques jours après expiration
  6. **Billing API** : Endpoints consultation factures, changement plan
  7. **Security** : Validation signatures webhooks Stripe

## Tâches Techniques Transversales

### T017V - Design System et composants (Vue)
- **US associée** : Transversal - Interface cohérente MangaCollec
- **Description** : Système de design complet et composants réutilisables
- **Critères d'acceptation** :
  - Charte graphique MangaCollec implémentée
  - Composants Tailwind CSS réutilisables
  - Thème sombre/clair + responsive complet
- **Estimation** : 8 points
- **Priorité** : Haute
- **📋 Résumé technique** :
  1. **Design tokens** : Variables CSS couleurs, tailles, espacements MangaCollec
  2. **Composants base** : Boutons, inputs, cards, modals réutilisables
  3. **Layout system** : Grilles, containers, spacing cohérents
  4. **Theme switcher** : Toggle dark/light avec persistence localStorage
  5. **Responsive utilities** : Breakpoints et utilities mobiles
  6. **Icon system** : SVG icons cohérents et accessibles
  7. **Typography scale** : Hiérarchie typographique complète

### T017L - Base de données et modèles (Logique)
- **US associée** : Transversal - Structure de données complète
- **Description** : Tous les modèles Django selon MCD avec relations
- **Critères d'acceptation** :
  - Modèles conformes au MCD PlantUML
  - Relations et contraintes correctes
  - Migrations et fixtures de test
- **Estimation** : 10 points
- **Priorité** : Haute
- **📋 Résumé technique** :
  1. **Modèles core** : Series, Volume, Author, Publisher, Genre, Kind
  2. **Modèles utilisateur** : User étendu, Possession, Read, UserPreferences
  3. **Relations complexes** : ManyToMany avec through models si nécessaire
  4. **Contraintes métier** : Validations, unique_together, indexes
  5. **UUID primary keys** : Sécurité et évolutivité
  6. **Model methods** : __str__, get_absolute_url, propriétés métier
  7. **Fixtures données** : Données test pour développement

### T018L - Tests et qualité (Logique)
- **US associée** : Transversal - Fiabilité et maintenabilité du système
- **Description** : Suite de tests complète avec couverture >80%
- **Critères d'acceptation** :
  - Tests unitaires modèles, vues, APIs
  - Tests intégration workflows complets
  - Tests permissions par rôle User/Premium
- **Estimation** : 12 points
- **Priorité** : Moyenne
- **📋 Résumé technique** :
  1. **Tests models** : Validation contraintes, méthodes, relations
  2. **Tests APIs** : Endpoints, permissions, codes retour, serialization
  3. **Tests auth** : Inscription, connexion, permissions rôles
  4. **Tests business logic** : Ajout/suppression, statistiques, recommandations
  5. **Test fixtures** : Factory Boy pour données test cohérentes
  6. **Integration tests** : Workflows complets utilisateur
  7. **Coverage reporting** : Configuration coverage.py >80%

---

## 📊 Récapitulatif Final

### **Répartition Vue/Logique**
- **Tâches VIEW (V)** : 16 tâches - **71 points**
- **Tâches LOGIC (L)** : 18 tâches - **105 points**
- **Total** : **34 tâches - 176 points**

### **Répartition par priorité**
- **Haute** : 16 tâches (94 points)
- **Moyenne** : 12 tâches (64 points)  
- **Basse** : 6 tâches (22 points)

### **Fonctionnalités Premium**
- 6 tâches spécifiques Premium (View + Logic)
- Contrôle d'accès par middleware

### **Architecture moderne**
- ✅ **Séparation claire** Vue/Logique
- ✅ **IDs cohérents** T001V/T001L
- ✅ **Développement parallèle** Frontend/Backend
- ✅ **Tests ciblés** par domaine
- ✅ **Réutilisabilité** composants + APIs