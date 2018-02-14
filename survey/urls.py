from django.conf.urls import url
from . import views

app_name = 'survey'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new_survey_form$', views.new_survey_form, name='new_survey_form'),
    url(r'^publish_new_survey$', views.publish_new_survey, name='publish_new_survey'),
    url(r'^survey_listing_page$', views.survey_listing_page, name='survey_listing_page'),
    url(r'^delete_survey$', views.delete_survey, name='delete_survey'),
    url(r'^broadcast_survey$', views.broadcast_survey, name='broadcast_survey'),
    url(r'^get_survey_analysis/(?P<survey_id>[0-9]+)/$', views.get_survey_analysis, name='get_survey_analysis')
]


