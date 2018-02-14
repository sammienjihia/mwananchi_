from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from region.models import Country, County, Constituency, Ward
from client.models import Client

# Create your models here.


class Volunteer(models.Model):
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    region_name = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(null=False, blank=False)

    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.CASCADE)
    county = models.ForeignKey(County, null=True, blank=True, on_delete=models.CASCADE)
    constituency = models.ForeignKey(Constituency, null=True, blank=True, on_delete=models.CASCADE)
    ward = models.ForeignKey(Ward, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Volunteer'
        unique_together = ('client', 'phone_number')


