from django.db import models
import uuid


class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    to_display = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        ordering = ['title']

class Kind(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Kind"
        verbose_name_plural = "Kinds"
        ordering = ['title']

class Publisher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)

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

    class Meta:
        verbose_name = "Serie"
        verbose_name_plural = "Series"
        ordering = ['title']

class Volume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    number = models.IntegerField(default=1)
    release_date = models.DateField()
    isbn = models.CharField()
    possessions_count = models.IntegerField(default=0)
    image_url = models.TextField(default='cover.png')
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE)


    class Meta:
        verbose_name = "Volume"
        verbose_name_plural = "Volumes"
        ordering = ['title', 'number']
        