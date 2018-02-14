from django.db import models

# Create your models here.


class Seat(models.Model):
    seat_name = models.CharField(max_length=50, unique=True, null=False, blank=False)
    short_code = models.CharField(max_length=15, unique=True, null=False, blank=False)
    date = models.DateTimeField(auto_now=True),

    class Meta:
        db_table = 'Seat'

    def __str__(self):
        return self.seat_name



