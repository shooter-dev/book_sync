from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
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
