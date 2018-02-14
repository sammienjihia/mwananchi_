from django.conf.urls import url
from django.conf.urls.static import static
from accounts.views import settings
from . import views

app_name = 'accounts'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index$', views.index, name='index'),
    url(r'^login_page$', views.login_page, name='login_page'),
    url(r'^login_user$', views.login_user, name='login_user'),
    url(r'^logout_user$', views.logout_user, name='logout_user'),
    url(r'^check_email_exists$', views.check_email_exists, name='check_email_exists'),
    url(r'^change_password$', views.change_password, name='change_password'),
    url(r'^landing_page$', views.landing_page, name='landing_page'),
    url(r'^profile_page$', views.profile_page, name='profile_page'),
    url(r'^upload_profile_picture$', views.upload_profile_picture, name='upload_profile_picture'),
    url(r'^settings_page$', views.settings_page, name='settings_page'),
    url(r'^authorize_twitter$', views.authorize_twitter, name='authorize_twitter'),
    url(r'^authorize_twitter/authenticated/?$', views.twitter_authenticated, name='twitter_authenticated'),
    url(r'^disconnect_twitter_account$', views.disconnect_twitter_account, name='disconnect_twitter_account'),
    url(r'^set_password/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', views.PasswordResetView.as_view(),name='set_password'),
    url(r'^reset_password/',views.ResetPasswordRequestView.as_view(), name="reset_password"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

