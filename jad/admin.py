from django.contrib import admin

from jad.models import JadRelation


@admin.register(JadRelation)
class JadRelation(admin.ModelAdmin):
    list_display = ["id", "source_id", "target_id", "distance"]
