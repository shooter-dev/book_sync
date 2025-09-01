## Documentation d’intégration PostgreSQL
---
# 🎯 Objectif
Cette documentation décrit l’intégration de la base PostgreSQL dans le projet BookSync. Elle s’appuie sur le MCD (Modèle Conceptuel de Données) défini en UML et détaille :

La structure des entités et leurs relations

Les modèles Django correspondants

Des exemples de requêtes ORM utiles pour le backend
---
## 🧩 Structure du MCD
BookSync repose sur une base relationnelle modulaire, pensée pour la gestion de collections, les préférences utilisateur, et les recommandations IA.

# 🧱 Entités principales

|     users      | Utilisateurs (profil, email, mot de passe) |
|:--------------:|------------------------------------------:|
|     roles      |      ARôles d’accès (admin, premium, etc.) |
|       users_roles      |     Liaison N-N entre utilisateurs et rôles                                      |
|      series    |          Séries de livres ou mangas                                 |
|       volumes         |         Tomes individuels liés à une série                                  |
|      possessions          |      Volumes possédés par un utilisateur                      |
|       partages         |           Système d’amis entre utilisateurs                                |
|      genres / kinds          |         Catégories et types narratifs                                  |
|      like_genres / dislike_genres          |             Préférences utilisateur                              |
|     like_kinds / dislike_kinds           |          Préférences utilisateur                                 |
|      publisher          |     Maison d’édition                                      |
|       authors / jobs / tasks      |              	Métadonnées éditoriales (auteur, rôle, contribution)                             |

---

🔗 Relations clés

* users → users_roles → roles : N-N

* users → possessions → volumes → series

* users → partages (user ↔ ami)

* series → volumes

* series → publisher, genres, kinds

* users → like_genres, dislike_genres, like_kinds, dislike_kinds

* authors → tasks → series + jobs

---
	
## 🧬 Modèles Django (extraits)

User
```console
class User(models.Model):
    pseudo = models.CharField(max_length=30)
    email = models.EmailField()
    password = models.CharField(max_length=128)
    roles = models.ManyToManyField("Role", through="UserRole")

```
	
Serie et Volume
```console
class Serie(models.Model):
    title = models.CharField(max_length=255)
    publisher = models.ForeignKey("Publisher", on_delete=models.SET_NULL, null=True)
    genre = models.ForeignKey("Genre", on_delete=models.SET_NULL, null=True)
    adult_content = models.BooleanField(default=False)

class Volume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=30)
    number = models.IntegerField()
    release_date = models.DateField()
    isbn = models.CharField(max_length=13)
    possessions_count = models.IntegerField(default=0)
    image_url = models.URLField()
    serie = models.ForeignKey("Serie", on_delete=models.CASCADE)
```
	
Possession
```console
class Possession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    volume = models.ForeignKey("Volume", on_delete=models.CASCADE)
    ajouter_le = models.DateTimeField(auto_now_add=True)
```
---

## 🧪 Exemples de requêtes ORM
# 🔹 Volumes possédés mais non lus
```console
Volume.objects.filter(
    possession__user=user
).exclude(
    read__user=user
)
```

# 🔹 Séries d’un utilisateur
```console
Serie.objects.filter(
    volume__possession__user=user
).distinct()
```
# 🔹 Préférences utilisateur
```console
user.like_genres.all()
user.dislike_kinds.all()
```
# 🔹 Ajouter une possession
```console
Possession.objects.create(user=user, volume=volume)
```
# 🔹 Rechercher les volumes d’une série
```console
Volume.objects.filter(serie__title="Naruto").order_by("number")
```
---
## 🛠️ Optimisations PostgreSQL

* Clés primaires en UUID pour sécurité et scalabilité

* Index sur les champs relationnels (user_id, volume_id, serie_id)

* Requêtes optimisées avec select_related() et prefetch_related()

* Dénormalisation partielle : possessions_count dans Volume

* Profiling avec EXPLAIN ANALYZE pour les requêtes critiques

---

## 📦 Migrations & Initialisation

```Console
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata fixtures/initial_data.json
```
---

## ✅ Résultat attendu
Une base PostgreSQL robuste, normalisée, et optimisée pour :

* La gestion des collections et lectures

* Le traitement des préférences utilisateur

* L’alimentation du moteur de recommandation IA
