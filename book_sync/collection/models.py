from django.db import models
from django.conf import settings
import uuid

class Authors(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255,blank=True, null=True)

    def __str__(self):
        if self.first_name is None:
            return self.name
        else:
            return f"{self.name} {self.first_name}"

    def __repr__(self):
        if self.first_name is None:
            return self.name
        else:
            return f"{self.name} {self.first_name}"

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        ordering = ['name']


class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    to_display = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        ordering = ['title']


class Kind(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    class Meta:
        verbose_name = "Kind"
        verbose_name_plural = "Kinds"
        ordering = ['title']


class Publisher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    class Meta:
        verbose_name = "Publisher"
        verbose_name_plural = "Publishers"
        ordering = ['title']


class Serie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    adult_content = models.BooleanField(default=False)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    kinds = models.ManyToManyField(Kind, blank=True)
    #author = models.ForeignKey(Authors, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    class Meta:
        verbose_name = "Serie"
        verbose_name_plural = "Series"
        ordering = ['title']


class Volume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    number = models.IntegerField(default=1)
    release_date = models.DateField(null=True, blank=True)
    isbn = models.CharField(null=True, blank=True)
    possessions_count = models.IntegerField(default=0)
    image_url = models.TextField(default='cover.png', null=True, blank=True)
    content = models.TextField(default='...', null=True, blank=True)
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.serie.title} - Tome {self.number}: {self.title}"

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    class Meta:
        verbose_name = "Volume"
        verbose_name_plural = "Volumes"
        ordering = ['serie__title', 'number']


class Jobs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Job"
        verbose_name_plural = "Jobs"
        ordering = ["title"]


class Tasks(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_author = models.ForeignKey(Authors, on_delete=models.CASCADE)
    id_jobs = models.ForeignKey(Jobs, on_delete=models.CASCADE)
    id_serie = models.ForeignKey(Serie, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "task"
        verbose_name_plural = "tasks"
        ordering = ["id"]


class Possession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='possessions')
    volume = models.ForeignKey(Volume, on_delete=models.PROTECT, related_name='user_possessions')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} possède {self.volume}"

    class Meta:
        verbose_name = "Possession"
        verbose_name_plural = "Possessions"
        unique_together = ('user', 'volume')
        ordering = ['-created_at']



class like_kind(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)# , related_name='user_')
    kind = models.ForeignKey(Kind, on_delete=models.PROTECT) # , related_name='user_like_kind')
    like = models.BooleanField(default=True)

    def __str__(self):
        if self.like:
            return f"{self.user.username} aime {self.kind.title}"
        return f"{self.user.username} n'aime pas {self.kind.title}"

    class Meta:
        unique_together = ('user', 'kind')


class like_genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT)
    like = models.BooleanField(default=True)

    def __str__(self):
        if self.like:
            return f"{self.user.username} aime {self.genre.title}"
        return f"{self.user.username} n'aime pas {self.genre.title}"

    class Meta:
        unique_together = ('user', 'genre')