from django.db import models
from client.models import Client
from language.models import Language
from subscribers.models import Subscriber

# Create your models here.


class Campaign(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    language = models.ForeignKey(Language)
    title = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Campaign'
        unique_together = ('client', 'language')

    def get_campaign_title(self, user_id):
        campaign_obj = Campaign.objects.filter(user_id=user_id).first().values()
        return campaign_obj['title']

    def client_has_campaign(self, client):
        num_of_campaign = Campaign.objects.filter(client=client).count()
        if num_of_campaign > 0:
            return True
        else:
            return False

    def get_campaign_id(self, client):
        campaign_obj = Campaign.objects.filter(client=client).values('id')
        return campaign_obj


class CampaignItems(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.CharField(max_length=1000)
    date_created = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CampaignItems'
        unique_together = ('campaign', 'title')


class CampaignItemsReception(models.Model):
    campaign_item = models.ForeignKey(CampaignItems, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, null=True, blank=True)
    date_read = models.DateTimeField(auto_now=True)

    class Meta:
        db_table='CampaignItemsReception'


