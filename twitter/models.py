from __future__ import unicode_literals

from django.db import models
from client.models import Client

# Create your models here.


class TwitterTimeline(models.Model):
    aspirant = models.ForeignKey(Client, null=True, blank=True)
    status_id = models.CharField(max_length=100, null=True, blank=True)
    status_text = models.CharField(max_length=10000, null=True, blank=True)
    retweet_count = models.IntegerField(null=True, blank=True, default=0)
    in_reply_to_status_id = models.CharField(max_length=100, null=True, blank=True)
    in_reply_to_status_text = models.CharField(max_length=100, null=True, blank=True)
    in_reply_to_screen_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    favourite = models.IntegerField(null=True, blank=True, default=0)
    followers = models.IntegerField(null=True, blank=True, default=0)
    tweet_sentiment = models.CharField(max_length=20, null=True, blank=True)
    polarity = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'TwitterTimeline'


class TwitterMentions(models.Model):
    aspirant = models.ForeignKey(Client, null=True, blank=True)
    status_id = models.CharField(max_length=100, null=True, blank=True)
    status_text = models.CharField(max_length=10000, null=True, blank=True)
    retweet_count = models.IntegerField(null=True, blank=True, default=0)
    in_reply_to_status_id = models.CharField(max_length=100, null=True, blank=True)
    in_reply_to_status_text = models.CharField(max_length=100, null=True, blank=True)
    in_reply_to_screen_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    favourite = models.IntegerField(null=True, blank=True, default=0)
    followers = models.IntegerField(null=True, blank=True, default=0)
    tweet_sentiment = models.CharField(max_length=20, null=True, blank=True)
    polarity = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'TwitterMentions'


class TwitterResult(models.Model):
    aspirant = models.ForeignKey(Client, null=True, blank=True)
    key_word = models.CharField(max_length=140, null=True, blank=True)
    tweet_id = models.CharField(max_length=100, null=True, blank=True)
    text = models.CharField(max_length=10000, null=True, blank=True)
    author = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    followers = models.IntegerField(null=True, blank=True, default=0)
    retweet = models.IntegerField(null=True, blank=True, default=0)
    favourite = models.IntegerField(null=True, blank=True, default=0)
    tweet_sentiment = models.CharField(max_length=20, null=True, blank=True)
    polarity = models.FloatField(null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    place = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'TwitterResult'






