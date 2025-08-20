import uuid

from django.contrib.auth.models import User
from django.db import models

from collection.models import Volume


class Read(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='user_read_read')
    volume = models.ForeignKey(Volume, on_delete=models.PROTECT, related_name='user_read_volume')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} a lu {self.volume}"

    class Meta:
        verbose_name = "Read"
        verbose_name_plural = "Reads"
        unique_together = ('user', 'volume')
        ordering = ['-created_at']
