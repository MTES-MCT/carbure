from django.db import models


class Feedstock(models.Model):
    matiere_premiere = models.ForeignKey("core.MatierePremiere", on_delete=models.CASCADE)
    classification = models.ForeignKey("feedstocks.Classification", on_delete=models.CASCADE)
    name = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return f"{self.name} - {self.classification}"

    class Meta:
        db_table = "feedstock"
        verbose_name = "Feedstock"
        verbose_name_plural = "Feedstocks"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"{self.matiere_premiere.name}"
        super().save(*args, **kwargs)
