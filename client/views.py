import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from volunteer.models import Volunteer
from subscribers.models import Subscriber
from sms.models import Inbox, Outbox
from client.models import Client

# Create your views here.

def index(request):
    pass


@login_required(login_url='accounts:login_page')
def get_landing_page_data(request):
    return_data = {
        'num_of_volunteers': Volunteer.objects.filter(client=Client.objects.get(user=request.user)).count(),
        'num_of_subscribers': Subscriber.objects.filter(client=Client.objects.get(user=request.user)).count(),
        'interactions': [],
        'num_of_inbox_sms': Inbox.objects.filter(user=request.user).count(),
        'num_of_outbox_sms': Outbox.objects.filter(user=request.user).count()
    }
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def edit_slogan(request):
    password = request.POST.get('password')
    return_data = {}
    if not request.user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        slogan = request.POST.get('slogan')
        client = Client.objects.get(user=request.user)
        client.slogan = slogan
        try:
            client.save()
            return_data['STATUS'] = '1'
            return_data['MESSAGE'] = 'Slogan has been updated'
        except:
            return_data['STATUS'] = '0'
            return_data['MESSAGE'] = 'As error occurred'

    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def edit_region_name(request):
    password = request.POST.get('password')
    return_data = {}
    if not request.user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        region_name = request.POST.get('region_name')
        client = Client.objects.get(user=request.user)
        client.region_name = region_name
        try:
            client.save()
            return_data['STATUS'] = '1'
            return_data['MESSAGE'] = 'Region name has been updated'
        except:
            return_data['STATUS'] = '0'
            return_data['MESSAGE'] = 'As error occurred'

    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def edit_alias_name(request):
    password = request.POST.get('password')
    return_data = {}
    if not request.user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        alias_name = request.POST.get('alias_name')
        client = Client.objects.get(user=request.user)
        client.alias_name = alias_name
        try:
            client.save()
            return_data['STATUS'] = '1'
            return_data['MESSAGE'] = 'Alias has been updated'
        except:
            return_data['STATUS'] = '0'
            return_data['MESSAGE'] = 'As error occurred'

    return HttpResponse(json.dumps(return_data))







