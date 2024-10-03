from django.db import models


class EntitySite(models.Model):
    OWN = "OWN"
    THIRD_PARTY = "THIRD_PARTY"
    PROCESSING = "PROCESSING"
    TYPE_OWNERSHIP = ((OWN, "Propre"), (THIRD_PARTY, "Tiers"), (PROCESSING, "Processing"))

    entity = models.ForeignKey("core.Entity", null=False, blank=False, on_delete=models.CASCADE)
    site = models.ForeignKey("transactions.Site", null=False, blank=False, on_delete=models.CASCADE)
    ownership_type = models.CharField(max_length=32, choices=TYPE_OWNERSHIP, default=THIRD_PARTY)
    blending_is_outsourced = models.BooleanField(default=False)
    blender = models.ForeignKey("core.Entity", null=True, blank=True, on_delete=models.CASCADE, related_name="blender")

    def __str__(self):
        return str(self.id)

    def natural_key(self):
        from transactions.models import Site

        if self.site.site_type != Site.PRODUCTION_SITE:
            type = "depot"
        else:
            type = "site"
        return {
            type: self.site.natural_key(),
            "ownership_type": self.ownership_type,
            "blending_is_outsourced": self.blending_is_outsourced,
            "blender": self.blender.natural_key() if self.blender else None,
        }

    class Meta:
        db_table = "entity_site"
        verbose_name = "Site Entité"
        verbose_name_plural = "Sites Entités"
