from __future__ import unicode_literals

from django.db import models

# Create your models here.

class SubscriberdetailsQuestion(models.Model):
    question = models.CharField(max_length=255, null=False, blank=False)
    question_type = models.CharField(max_length=255, null=False, blank=False)
    allowed_options = models.CharField(max_length=10000, null=True, blank=True)
    options_mapping = models.CharField(max_length=10000, null=True, blank=True)

    class Meta:
        db_table = 'SubscriberdetailsQuestion'
