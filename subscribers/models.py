from django.db import models
from region.models import Country, County, Constituency, Ward
from client.models import Client
from volunteer.models import Volunteer
from language.models import Language

# Create your models here.


class Subscriber(models.Model):
    first_name = models.CharField(max_length=25, null=True, blank=True)
    last_name = models.CharField(max_length=25, null=True, blank=True)
    gender = models.CharField(max_length=6, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    current_age = models.FloatField(null=True, blank=True)
    phone_number = models.CharField(max_length=25, null=False, blank=False)
    email_address = models.CharField(max_length=100, null=True, blank=True)
    language = models.ForeignKey(Language, null=True, blank=True)
    is_active = models.BooleanField()

    client = models.ForeignKey(Client, null=True, blank=True)
    volunteer = models.ForeignKey(Volunteer, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    county = models.ForeignKey(County, null=True, blank=True)
    constituency = models.ForeignKey(Constituency, null=True, blank=True)
    ward = models.ForeignKey(Ward, null=True, blank=True)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Subscriber'
        unique_together = ('phone_number', 'client')

