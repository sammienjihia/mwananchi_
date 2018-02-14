from __future__ import unicode_literals

import datetime
import time

from django.db import models
from django.utils.timezone import now

from client.models import Client
from subscribers.models import Subscriber

# Create your models here.


class Survey(models.Model):
    survey_title = models.CharField(max_length=500, null=False, blank=False)
    survey_desc = models.CharField(max_length=10000)
    is_sent = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now=True)
    aspirant = models.ForeignKey(Client)


    class Meta:
        db_table = 'Survey'


class SurveyRecipient(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(Subscriber)
    date_created = models.DateTimeField(auto_now=True)
    has_been_notified  =models.BooleanField(default=False)
    date_notified = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'SurveyRecipient'


class SurveyQuestion(models.Model):
    question_number = models.IntegerField(max_length=10, null=True, blank=True)
    question = models.CharField(max_length=500, null=False, blank=False)
    date_created = models.DateTimeField(auto_now=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    class Meta:
        db_table = 'SurveyQuestion'
        unique_together = ('question_number', 'survey')


class SurveyOptions(models.Model):
    option = models.CharField(max_length=500, null=False, blank=False)
    date_created = models.DateTimeField(auto_now=True)
    survey_question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)

    class Meta:
        db_table = 'SurveyOptions'


class SurveyResponse(models.Model):
    date_answered = models.DateTimeField(auto_now=True)
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    survey_option = models.ForeignKey(SurveyOptions, on_delete=models.CASCADE)

    class Meta:
        db_table = 'SurveyResponse'
        unique_together = ('subscriber', 'survey_option')


