from django.conf.urls import url
from client import views

app_name = 'client'

urlpatterns = [
    url(r'^/$', views.index, name='index'),
    url(r'^index$', views.index, name='index'),
    url(r'^get_landing_page_data$', views.get_landing_page_data, name='get_landing_page_data'),
    url(r'^edit_slogan$', views.edit_slogan, name='edit_slogan'),
    url(r'^edit_region_name$', views.edit_region_name, name='edit_region_name'),
    url(r'^edit_alias_name$', views.edit_alias_name, name='edit_alias_name')
]