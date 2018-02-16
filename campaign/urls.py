from django.conf.urls import url
from . import views

app_name = 'campaign'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index$', views.index, name='index'),
    url(r'^campaign_reception_analysis/(?P<manifesto_id>[0-9]+)/$', views.manifesto_reception_analysis, name='manifesto_reception_analysis'),
    url(r'^edit_campaign_form/(?P<manifesto_id>[0-9]+)/$', views.edit_manifesto_form, name='edit_manifesto_form'),
    url(r'^new_campaign_form$', views.new_manifesto_form, name='new_manifesto_form'),
    url(r'^publish_new_campaign$', views.publish_new_manifesto, name='publish_new_manifesto'),
    url(r'^update_campaign$', views.update_manifesto, name='update_manifesto'),
    url(r'^broadcast_campaign$', views.broadcast_manifesto, name='broadcast_manifesto'),
    url(r'^delete_campaign$', views.delete_manifesto, name='delete_manifesto')
]
