from django.conf.urls import url
from . import views

app_name = 'sms'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^outbox_list$', views.outbox_list, name='outbox_list'),
    url(r'^outbox_list/(?P<offset>[0-9]+)/$', views.outbox_list, name='outbox_list'),
    url(r'^inbox_list$', views.inbox_list, name='inbox_list'),
    url(r'^inbox_list/(?P<offset>[0-9]+)/$', views.inbox_list, name='inbox_list'),
    url(r'^upload_recipients_excel_file$', views.upload_recipients_excel_file, name='upload_recipients_excel_file'),
    url(r'^send_batch_sms$', views.send_batch_sms, name='send_batch_sms'),
    url(r'^receive_sms/$', views.receive_sms, name='receive_sms'),
    url(r'^reply_to_single_message$', views.reply_to_single_message, name='reply_to_single_message'),
    url(r'^mark_as_read$', views.mark_as_read, name='mark_as_read'),
    url(r'^delete_batch_inbox$', views.delete_batch_inbox, name='delete_batch_inbox'),
    url(r'^reply_batch_inbox$', views.reply_batch_inbox, name='reply_batch_inbox'),
    url(r'^get_num_of_words$', views.get_num_of_words, name='get_num_of_words'),
    url(r'^inbox_analysis$',views.inbox_analysis,name='inbox_analysis'),
    url(r'^get_last_7_day_sms_count$', views.get_last_7_day_sms_count, name='get_last_7_day_sms_count'),
    url(r'^get_sentiment_analysis', views.get_sentiment_analysis, name='get_sentiment_analysis'),
]
