from django.db import models
from django.contrib.auth.models import User

from subscribers.models import Subscriber

# Create your models here.


class Outbox(models.Model):
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    message = models.CharField(max_length=1000, null=False, blank=False)
    message_type = models.CharField(max_length=20, null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    date_sent = models.DateTimeField()

    user = models.ForeignKey(User, null=True, blank=True)
    subscriber = models.ForeignKey(Subscriber, null=True, blank=True)

    class Meta:
        db_table = 'Outbox'


class Inbox(models.Model):
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    message = models.CharField(max_length=1000, null=False, blank=False)
    is_received = models.BooleanField(default=False)
    message_type = models.CharField(max_length=20, null=True, blank=True)
    date_received = models.DateTimeField()
    date_created = models.DateTimeField(auto_now=True)
    africastalking_msg_id = models.CharField(max_length=100, null=True, blank=True)
    polarity = models.FloatField(null=True, blank=True)
    subjectivity = models.FloatField(null=True, blank=True)
    sentiment = models.CharField(max_length=20, null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    user = models.ForeignKey(User, null=True, blank=True)
    subscriber = models.ForeignKey(Subscriber, null=True, blank=True)

    class Meta:
        db_table = 'Inbox'

    def __str__(self):
        return  self.date_received.strftime('%Y-%m-%d')


class SMSMenuLog(models.Model):
    date_created = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(max_length=100, blank=False, null=False)
    menu_type = models.CharField(max_length=50, blank=False, null=False)
    allowed_options = models.CharField(max_length=10000, blank=True, null=True)
    extra_info = models.CharField(max_length=10000, blank=True, null=True)

    class Meta:
        db_table = 'SMSMenuLog'
        unique_together = ('date_created', 'phone_number')



