from django.contrib.gis.db import models


class Page(models.Model):
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    meta_title = models.CharField(max_length=255)
    meta_keywords = models.CharField(max_length=255)
    meta_description = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name