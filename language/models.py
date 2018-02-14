from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Language(models.Model):
    name = models.CharField(max_length=20, unique=True, null=False, blank=False)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Language'

    def __str__(self):
        return self.name
