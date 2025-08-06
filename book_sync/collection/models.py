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

class Serie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    adult_content = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Serie"
        verbose_name_plural = "Series"
        ordering = ['title']
        