from django.conf.urls import url
from . import views
from site_admin.views import *
from django.conf.urls.static import static

app_name = 'site_admin'

urlpatterns = [
    url(r'^/$', views.index, name='index'),
    url(r'^index$', views.index, name='index'),
    url(r'^get_landing_page_data$', views.get_landing_page_data, name='get_landing_page_data'),
    url(r'^batch_upload_aspirant_form$', views.batch_upload_aspirant_form, name='batch_upload_aspirant_form'),
    url(r'^upload_batch_aspirants_file$', views.upload_batch_aspirants_file, name='upload_batch_aspirants_file'),
    url(r'^approve_batch_aspirants_upload$', views.approve_batch_aspirants_upload, name='approve_batch_aspirants_upload'),
    url(r'^single_client_registration_form$', views.single_aspirant_registration_form, name='single_aspirant_registration_form'),
    url(r'^get_client_info$', views.get_client_info, name='get_client_info'),
    url(r'^lock_client_account$', views.lock_client_account, name='lock_client_account'),
    url(r'^unlock_client_account$', views.unlock_client_account, name='unlock_client_account'),

    url(r'^get_constituency_by_county$', views.get_constituency_by_county, name='get_constituency_by_county'),
    url(r'^get_ward_by_constituency$', views.get_ward_by_constituency, name='get_ward_by_constituency'),
    url(r'^register_single_aspirant$', views.register_single_aspirant, name='register_single_aspirant'),
    url(r'^list_of_clients$', views.list_of_aspirants, name='list_of_aspirants'),
    url(r'^list_of_clients/(?P<offset>[0-9]+)/$', views.list_of_aspirants, name='list_of_aspirants'),
    url(r'^list_of_volunteers/(?P<offset>[0-9]+)/$', views.list_of_volunteers, name='list_of_volunteers'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)