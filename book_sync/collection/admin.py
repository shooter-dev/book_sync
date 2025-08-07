from django.contrib import admin

from . import models

class Seriesadmin(admin.ModelAdmin):
    list_display = ("title","genre","kind")

admin.site.register(models.Publisher)

admin.site.register(models.Serie)

admin.site.register(models.Kind)

admin.site.register(models.Volume)

admin.site.register(models.Genre)

admin.site.register(models.Authors)


