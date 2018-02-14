from django.conf.urls import url
from . import views

app_name = 'volunteer'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^opt_out_of_subscription$', views.opt_out_of_subscription, name='opt_out_of_subscription'),
    url(r'^get_share_volunteer_link', views.get_share_volunteer_link, name='get_share_volunteer_link'),
    url(r'^share_link_on_twitter$', views.share_link_on_twitter, name='share_link_on_twitter'),
    url(r'^volunteer_sign_up/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', views.VolunteerShareableLinkView.as_view(),
        name='volunteer_link'),
    url(r'^volunteer_list$', views.volunteer_list, name='volunteer_list'),
    url(r'^volunteer_list/(?P<offset>[0-9]+)/$', views.volunteer_list, name='volunteer_list'),

    url(r'^download_all_volunteers$', views.download_all_volunteers, name='download_all_volunteers'),

    url(r'^get_landing_page_data$', views.get_landing_page_data, name='get_landing_page_data')
]


