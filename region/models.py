from django.db import models

# Create your models here.


class Country(models.Model):
    country_name = models.CharField(max_length=255, null=False, unique=True)
    date_added = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Country'


class County(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    county_name = models.CharField(max_length=255, null=False, unique=True)
    date_added = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'County'

    def __str__(self):
        return self.county_name


class Constituency(models.Model):
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    constituency_name = models.CharField(max_length=255, null=False, blank=False)
    date_added = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Constituency'
        unique_together = ('county', 'constituency_name')

    def __str__(self):
        return self.constituency_name


class Ward(models.Model):
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    ward_name = models.CharField(max_length=255, null=False, blank=False)
    date_added = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Ward'
        unique_together = ('constituency', 'ward_name')

    def __str__(self):
        return self.ward_name






