"""BrandSense URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'', include('accounts.urls')),
    url(r'^site_admin/', include('site_admin.urls')),
    url(r'^client/', include('client.urls')),
    url(r'^volunteer/', include('volunteer.urls')),
    url(r'^subscriber/', include('subscribers.urls')),
    url(r'^campaign/', include('campaign.urls')),
    url(r'^sms/', include('sms.urls')),
    url(r'^survey/', include('survey.urls')),
    url(r'^twitter/', include('twitter.urls')),
]