from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Modèle utilisateur personnalisé avec support premium basé sur les groupes
    """

    age = models.IntegerField(blank=True, null=True, verbose_name="Âge")
    is_adult = models.BooleanField(default=False, verbose_name="18 ans ou plus")
    show_mature_content = models.BooleanField(default=False, verbose_name="Afficher contenu mature")
    
    @property
    def is_premium(self):
        """Vérifie si l'utilisateur fait partie du groupe premium"""
        return self.groups.filter(name='premium').exists()
    
    @property
    def can_access_mature_content(self):
        """Vérifie si l'utilisateur peut accéder aux paramètres de contenu mature (16 ans minimum)"""
        return self.age is not None and self.age >= 16

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        premium_status = " (Premium)" if self.is_premium else ""
        return f"{self.username}{premium_status}"
