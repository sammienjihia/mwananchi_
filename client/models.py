from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from region.models import Country, County, Constituency, Ward
from seats.models import Seat

# Create your models here.


class Client(models.Model):
    alias_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    region_name = models.CharField(max_length=200, null=False, blank=False)
    slogan = models.CharField(max_length=1000, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='PROFILE_PICS', null=True, blank=True)

    twitter_oauth_token = models.CharField(max_length=255, null=True, blank=True, default='')
    twitter_oauth_secret = models.CharField(max_length=255, null=True, blank=True, default='')
    twitter_screen_name = models.CharField(max_length=255, null=True, blank=True, default='')

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.CASCADE)
    county = models.ForeignKey(County, null=True, blank=True, on_delete=models.CASCADE)
    constituency = models.ForeignKey(Constituency, null=True, blank=True, on_delete=models.CASCADE)
    ward = models.ForeignKey(Ward, null=True, blank=True, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'Client'
        unique_together = ('region_name', 'seat')

