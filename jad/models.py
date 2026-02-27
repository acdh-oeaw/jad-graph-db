from django.db import models


class JadRelation(models.Model):
    source_id = models.CharField(max_length=250, verbose_name="Source ID")
    target_id = models.CharField(max_length=250, verbose_name="Target ID")
    distance = models.FloatField(verbose_name="selected max distance")

    class Meta:
        ordering = ["-id"]
        verbose_name = "Jad relation"
        verbose_name_plural = "Jad relations"
        unique_together = ("source_id", "target_id", "distance")

    def __str__(self):
        return f"{self.source_id}–{self.target_id} ({self.distance})"
