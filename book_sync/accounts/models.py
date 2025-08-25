from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_adult = models.BooleanField(default=True)
    show_mature_content = models.BooleanField(default=True)
    age = models.IntegerField(null=True, blank=True)

    """
    Modèle utilisateur personnalisé avec support premium basé sur les groupes
    """
    
    @property
    def is_premium(self):
        """Vérifie si l'utilisateur fait partie du groupe premium"""
        return self.groups.filter(name='premium').exists()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        premium_status = " (Premium)" if self.is_premium else ""
        return f"{self.username}{premium_status}"
