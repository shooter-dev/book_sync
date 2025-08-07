from django.contrib import admin

from . import models

admin.site.register(models.Publisher)

admin.site.register(models.Serie)

admin.site.register(models.Kind)

admin.site.register(models.Volume)

admin.site.register(models.Genre)

admin.site.register(models.Authors)
