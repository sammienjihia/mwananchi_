from django.conf.urls import url
from . import views


app_name ='subscribers'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^get_number_of_subscribers$', views.get_number_of_subscribers, name='get_number_of_subscribers'),
    url(r'^get_subscribers_count_on_filter$', views.get_subscribers_count_on_filter, name='get_subscribers_count_on_filter'),
    url(r'^get_subscribers_list_for_sms$', views.get_subscribers_list_for_sms, name='get_subscribers_list_for_sms'),

    url(r'^batch_upload_subscribers_form$', views.batch_upload_subscribers_form, name='batch_upload_subscribers_form'),
    url(r'^upload_subscribers_file', views.upload_subscribers_file, name='upload_subscribers_file'),
    url(r'^batch_approve_subscribers_from_file', views.batch_approve_subscribers_from_file, name="batch_approve_subscribers_from_file"),

    url(r'^single_upload_subscribers_form$', views.single_upload_subscribers_form, name='single_upload_subscribers_form'),
    url(r'^register_single_subscriber$', views.register_single_subscriber, name='register_single_subscriber'),

    url(r'^subscribers_list$', views.subscribers_list, name='subscribers_list'),
    url(r'^subscribers_list/(?P<offset>[0-9]+)/$', views.subscribers_list, name='subscribers_list'),
    url(r'^subscriber_analysis_by_gender', views.subscriber_analysis_by_gender, name='subscriber_analysis_by_gender'),
    url(r'^subscriber_analysis_by_age', views.subscriber_analysis_by_age, name='subscriber_analysis_by_age'),
    url(r'^subscriber_analysis_by_county', views.subscriber_analysis_by_county, name='subscriber_analysis_by_county'),
    url(r'^subscriber_analysis_by_ward', views.subscriber_analysis_by_ward, name='subscriber_analysis_by_ward'),
    url(r'^download_all_subscribers$', views.download_all_subscribers, name='download_all_subscribers'),
    url(r'^get_share_subscription_link', views.get_share_subscription_link, name='get_share_subscription_link'),
    url(r'^share_link_on_twitter$', views.share_link_on_twitter, name='share_link_on_twitter'),
    url(r'^subscribe_to_client/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', views.SubscribeShareableLinkView.as_view(),name='subscribe_link'),
]
