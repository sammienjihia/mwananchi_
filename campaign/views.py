import json
import datetime
from django.core import serializers

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q, Count


from client.models import Client
from language.models import Language
from campaign.models import Campaign, CampaignItems, CampaignItemsReception
from region.models import Ward
from subscribers.models import Subscriber


from app_utility.sms_utils import SMS

from collections import Counter
from operator import itemgetter
from celery_stuff.tasks import task_send_manifesto_to_subscribers


# Create your views here.


@login_required(login_url='accounts:login_page')
def index(request):
    template = 'campaign/index.html'
    context = {}
    num_of_manifestos = Campaign.objects.filter(client=Client.objects.get(user=request.user)).count()

    if num_of_manifestos == 0:
        context['has_manifesto'] = False
        context['languages'] = Language.objects.all()
    else:
        context['has_manifesto'] = True
        aspirant_manifestos = Campaign.objects.filter(client=Client.objects.get(user=request.user))

        context['aspirant_manifestos'] = []
        for manifesto in aspirant_manifestos:
            context['aspirant_manifestos'].append({
               'manifesto_title': manifesto.title,
               'manifesto_id': manifesto.id,
               'manifesto_items': CampaignItems.objects.filter(campaign=manifesto)
            })

        languages_used = [manifesto.language.id for manifesto in aspirant_manifestos]
        remaining_languages = Language.objects.exclude(id__in=languages_used)

        if len(remaining_languages) > 0:
            context['languages'] = remaining_languages
            context['can_add_manifesto'] = True
        else:
            context['can_add_manifesto'] = False
        print(context)
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def edit_manifesto_form(request, manifesto_id=1):
    manifesto = Campaign.objects.get(client=Client.objects.get(user=request.user), id=manifesto_id)
    template = 'campaign/edit_manifesto.html'
    context = {
        'campaign': manifesto,
        'manifesto_items': CampaignItems.objects.filter(campaign=manifesto),
        'languages': Language.objects.all()
    }
    return render(request, template, context)


def manifesto_reception_analysis(request, manifesto_id):
    template = 'campaign/manifesto_reception_analysis.html'
    manifesto = Campaign.objects.get(id=manifesto_id)
    manifesto_items = CampaignItems.objects.filter(campaign=manifesto)
    manifesto_recipients_count = []

    def get_age(dob):
        age = datetime.datetime.today().year - dob.year\
            - ((datetime.datetime.today().month, datetime.datetime.today().day)\
                < (dob.month, dob.day))
        return age

    for item in manifesto_items:
        manifesto_reception_items = CampaignItemsReception.objects.filter(campaign_item=item).distinct('subscriber')
        subscriber_ids = [manifesto_reception_item.subscriber.id for manifesto_reception_item in manifesto_reception_items]
        subscribers_gender = Subscriber.objects.filter(id__in=subscriber_ids).values('gender').annotate(num=Count('gender')).exclude(gender__isnull=True)
        subscribers_age = Subscriber.objects.filter(id__in=subscriber_ids).values('date_of_birth').exclude(date_of_birth__isnull=True)
        subscribers_ward = Subscriber.objects.filter(id__in=subscriber_ids).values('ward').annotate(num=Count('ward'))

        gender_analysis = []
        for obj in subscribers_gender:
            gender_analysis.append({
                'gender': obj['gender'],
                'num': obj['num']
            })

        age_arr = []
        try:
            for subscriber in subscribers_age:
                age_arr.append(get_age(subscriber['date_of_birth']))
        except:
            pass

        age_keys = list(Counter(age_arr).keys())
        age_count_values = list(Counter(age_arr).values())
        temp_items = []
        for i in range(0, len(age_keys)):
            temp_items.append({
                'age': age_keys[i],
                'num': age_count_values[i]
            })
        age_analysis = sorted(temp_items, key=itemgetter('age'))

        ward_analysis = []

        for obj in subscribers_ward:
            try:
                ward = Ward.objects.get(id=obj['ward'])
                ward_analysis.append({
                    'wardName': ward.ward_name,
                    'num': obj['num']
                })
            except:
                pass
        print(ward_analysis)
        manifesto_recipients_count.append({
            'manifesto_item': item.title,
            'item_id': item.id,
            'count': manifesto_reception_items.count(),
            'gender_analysis': gender_analysis,
            'age_analysis': age_analysis,
            'ward_analysis': ward_analysis
        })

    context = {
        'manifesto': manifesto,
        'manifesto_recipients_count': manifesto_recipients_count
    }
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def new_manifesto_form(request):
    template = 'campaign/new_campaign.html'
    context = {}
    num_of_manifestos = Campaign.objects.filter(client=Client.objects.get(user=request.user)).count()

    if num_of_manifestos == 0:
        context['has_manifesto'] = False
        context['languages'] = Language.objects.all()
    else:
        context['has_manifesto'] = True
        aspirant_manifesto = Campaign.objects.filter(client=Client.objects.get(user=request.user))
        languages_used = [manifesto.language.id for manifesto in aspirant_manifesto]
        remaining_languages = Language.objects.exclude(id__in=languages_used)

        if len(remaining_languages) > 0:
            context['languages'] = remaining_languages
            context['can_add_manifesto'] = True
        else:
            context['can_add_manifesto'] = False

    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def publish_new_manifesto(request):
    password = request.POST.get('password')
    return_data = {}

    if not request.user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        return_data['MESSAGE'] = []
        manifesto_title = request.POST.get('manifestoTitle')
        manifesto_language = request.POST.get('manifestoLanguage')

        manifesto = Campaign()
        manifesto.title = manifesto_title
        manifesto.client = Client.objects.get(user=request.user)
        manifesto.language = Language.objects.get(id=manifesto_language)
        manifesto.date_created = datetime.datetime.now()
        manifesto.save()
        try:
            manifesto.save()
            return_data['MESSAGE'].append({
                'STATUS': '1',
                'MESSAGE': 'Campaign has been created'
            })
            manifesto = Campaign.objects.get(client= Client.objects.get(user=request.user),
                                             language=manifesto_language,
                                             title=manifesto_title)
            manifesto_content = json.loads(request.POST.get('manifestoContent'))
            for item in manifesto_content:
                try:
                    manifesto_item = CampaignItems()
                    manifesto_item.campaign = manifesto
                    manifesto_item.title = item['contentTitle']
                    manifesto_item.content = item['content']
                    manifesto_item.save()
                    return_data['MESSAGE'].append({
                        'STATUS': '1',
                        'MESSAGE': '{} has been added to campaign.'.format(item['contentTitle'])
                    })
                except:
                    return_data['MESSAGE'].append({
                        'STATUS': '0',
                        'MESSAGE': '{} could not be added to the campaign.'.format(item['contentTitle'])
                    })
        except:
            return_data['MESSAGE'].append({
                'STATUS': '0',
                'MESSAGE': 'Campaign failed to be published'
            })

    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def update_manifesto(request):
    return_data = {}
    password = request.POST.get('password')
    if not request.user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        return_data['MESSAGE'] = []
        manifesto_id = request.POST.get('manifesto_id')
        manifesto_title = request.POST.get('manifestoTitle')


        manifesto_obj = Campaign.objects.get(id=manifesto_id, client=Client.objects.get(user=request.user))
        manifesto_obj.title = manifesto_title
        manifesto_obj.date_created = datetime.datetime.now()
        try:
            manifesto_obj.save()
            return_data['MESSAGE'].append({
                'STATUS': '1',
                'MESSAGE': 'Campaign has been updated'
            })
            # delete campaign items objects

            CampaignItems.objects.filter(campaign=Campaign.objects.get(
                        id=manifesto_id,
                        client=Client.objects.get(user=request.user))
                    ).delete()
            manifesto_content = json.loads(request.POST.get('manifestoContent'))
            for content in manifesto_content:
                manifesto_item = CampaignItems()
                manifesto_item.campaign = manifesto_obj
                manifesto_item.title = content['contentTitle']
                manifesto_item.content = content['content']
                manifesto_item.date_created = datetime.datetime.now()
                try:
                    manifesto_item.save()
                    return_data['MESSAGE'].append({
                        'STATUS': '1',
                        'MESSAGE': '{} has been added to campaign.'.format(content['contentTitle'])
                    })
                except:
                    return_data['MESSAGE'].append({
                        'STATUS': '0',
                        'MESSAGE': '{} has been added to campaign.'.format(content['contentTitle'])
                    })

        except:
            return_data['MESSAGE'].append({
                'STATUS': '0',
                'MESSAGE': 'Campaign failed to be updated'
            })
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def broadcast_manifesto(request):
    password = request.POST.get('password')
    return_data = {}

    if not request.user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        manifesto_id = request.POST.get('manifesto_id')
        aspirant = Client.objects.get(user=request.user)
        manifesto = Campaign.objects.get(client=aspirant, id=manifesto_id)
        sms_utils = SMS()
        aspirant = serializers.serialize('json', [aspirant, ])
        manifesto = serializers.serialize('json', [manifesto, ])

        # Celerify this function call
        #sms_utils.send_manifesto_to_subscribers(campaign, client)
        task_send_manifesto_to_subscribers.delay(manifesto, aspirant)

        return_data['STATUS'] = '1'
        return_data['MESSAGE'] = """
                Campaign shall be sent to all you subscribers.
            """
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def delete_manifesto(request):
    password = request.POST.get('password')
    return_data = {}

    if not request.user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        manifesto_id = request.POST.get('manifesto_id')
        return_data['MESSAGE'] = []
        manifesto = Campaign.objects.get(id=manifesto_id, client=Client.objects.get(user=request.user))
        try:
            CampaignItems.objects.filter(campaign=manifesto).delete()
            return_data['MESSAGE'].append({
                'STATUS': '1',
                'MESSAGE': 'Campaign items have been deleted'
            })
            try:
                manifesto.delete()
                return_data['MESSAGE'].append({
                    'STATUS': '1',
                    'MESSAGE': 'Campaign has been deleted'
                })
            except:
                return_data['MESSAGE'].append({
                    'STATUS': '0',
                    'MESSAGE': 'Failed to delete campaign'
                })
        except:
            return_data['MESSAGE'].append({
                'STATUS': '0',
                'MESSAGE': 'Failed to delete campaign items'
            })

    return HttpResponse(json.dumps(return_data))




