import json
import pyexcel
import os
import time
import datetime

from collections import Counter
from operator import itemgetter

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from django.template import loader
from django.template.loader import get_template
from django.template import Context


from app_utility.excel_utils import ExcelFile
from app_utility.sms_utils import SMS
from app_utility.email_utils import SendEmail

from client.models import Client
from region.models import Country, County, Constituency, Ward
from seats.models import Seat
from subscribers.models import Subscriber
from volunteer.models import Volunteer
from sms.models import Inbox, Outbox



#Create your views here.


@login_required(login_url='accounts:login_page')
def index(request):
    pass


@login_required(login_url='accounts:login_page')
def get_landing_page_data(request):
    return_data = {
        'num_of_volunteers': Volunteer.objects.count(),
        'num_of_aspirants': Client.objects.count(),
        'num_of_subscribers': Subscriber.objects.count(),
        'interactions': [],
        'num_of_inbox_sms': Inbox.objects.count(),
        'num_of_outbox_sms': Outbox.objects.count()
    }
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def batch_upload_aspirant_form(request):
    template = 'site_admin/batch_upload_aspirant_form.html'
    return render(request, template, {})


@login_required(login_url='accounts:login_page')
def upload_batch_aspirants_file(request):
    uploaded_file = request.FILES['file']
    tep_file_name = uploaded_file.name
    file_content_type = uploaded_file.content_type
    file_extension = file_content_type.split('/')[1]
    file_size = uploaded_file.size
    uploads_dir = 'ASPIRANTS_DIR'

    try:
        os.path.join(settings.MEDIA_ROOT, uploads_dir)
    except:
        pass

    file_name = str(int(time.time())) + '.' + file_extension
    full_file_name = os.path.join(settings.MEDIA_ROOT, uploads_dir, file_name)
    file_save = FileSystemStorage()
    saved_file_name = file_save.save(full_file_name, uploaded_file)

    request.session['ASPIRANTS_FILE_URL'] = full_file_name

    return_data = {
        'TMP_FILE_NAME': tep_file_name,
        'FILE_NAME': file_name,
        'file_size': file_size,
        'file_content_type': file_content_type
    }

    excel_file = ExcelFile(request.session['ASPIRANTS_FILE_URL'])
    headers = excel_file.get_header()

    allowed_headers = [
        'First name',
        'Last name',
        'Alias name'
        'Mobile number',
        'Email address'
        'Seat',
        'Region name',
        'County',
        'Constituency',
        'Ward'
    ]

    return_data['NUM_OF_RECORDS'] = excel_file.get_num_of_records() - 1
    return_data['HEADER'] = headers

    return_data['STATUS'] = '1'
    records = excel_file.get_records(True)
    return_data['DATA_LIST'] = []
    for record in records:
        record = list(record)
        return_data['DATA_LIST'].append({
            'firstName': record[0],
            'lastName': record[1],
            'aliasName': record[2],
            'mobileNumber': record[3],
            'emailAddress': record[4],
            'seat': record[5],
            'regionName': record[6],
            'county': record[7],
            'constituency': record[8],
            'ward': record[9]
        })

    return HttpResponse(
        json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def approve_batch_aspirants_upload(request):
    password = request.POST.get('password')
    return_data = {}
    if not request.user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        return_data['ASPIRANTS_REG'] = []
        excel_file = ExcelFile(request.session['ASPIRANTS_FILE_URL'])
        records = excel_file.get_records(True)
        for record in records:
            record = list(record)
            aspirant_reg = {'full_name': '{} {}'.format(record[0], record[1])}
            try:
                user_create = User.objects.create_user(
                        first_name=record[0],
                        last_name=record[1],
                        username=record[4],
                        email=record[4],
                        is_superuser=False,
                        is_staff=True,
                        date_joined=datetime.datetime.now()
                )
                aspirant_reg['registered_as_user'] = '1'
                aspirant = Client()
                aspirant.alias_name = record[2]
                aspirant.phone_number = SMS.format_phone_number(record[3])
                aspirant.user = User.objects.get(username=record[4])
                aspirant.seat = Seat.objects.get(Q(seat_name__icontains=record[5]) | Q(short_code__icontains=record[5]))
                aspirant.region_name = record[6]
                aspirant.country = Country.objects.get(country_name='Kenya')
                aspirant.county = County.objects.get(county_name=record[7])
                aspirant.constituency = Constituency.objects.get(constituency_name=record[8])
                aspirant.ward = Ward.objects.get(ward_name=record[9])
                try:
                    aspirant.save()
                    aspirant_reg['registered_as_aspirant'] = '1'
                except:
                    aspirant_reg['registered_as_aspirant'] = '0'
            except:
                aspirant_reg['registered_as_user'] = '0'

            return_data['ASPIRANTS_REG'].append(aspirant_reg)

    return HttpResponse(
        json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def single_aspirant_registration_form(request):
    template = 'site_admin/single_aspirant_registration_form.html'
    context = {
        'county_list': County.objects.all(),
        'seat_list': Seat.objects.all()
    }
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def get_client_info(request):
    client_id = request.POST.get('client_id')
    client = Client.objects.get(id=client_id)
    user_obj = User.objects.get(id=client.user.id)
    return_data = {
        'client_id': client_id,
        'is_active': 1 if client.user.is_active  else 0,
        'full_name': '{} {}'.format(user_obj.first_name, user_obj.last_name),
        'email_address': user_obj.email,
        'user_name': user_obj.username,
        'phone_number': client.phone_number,
        'number_of_subscribers': Subscriber.objects.filter(client=client).count(),
        'seat_name': client.seat.seat_name,
        'seat_code': client.seat.short_code,
        'region': client.region_name,
        'county': client.county.county_name
    }

    try:
        return_data['profile_picture'] = client.profile_picture.url
    except:
        pass

    try:
        return_data['constituency'] = client.constituency.constituency_name
    except:
        pass

    try:
        return_data['ward'] = client.ward.ward_name
    except:
        pass

    return HttpResponse(json.dumps(return_data))

@login_required(login_url='accounts:login_page')
def lock_client_account(request):
    client_id = request.POST.get('client_id')
    client = Client.objects.get(id=client_id)
    client.user.is_active = False
    client.user.save()
    return HttpResponse(json.dumps({'status':1}))

@login_required(login_url='accounts:login_page')
def unlock_client_account(request):
    client_id = request.POST.get('client_id')
    client = Client.objects.get(id=client_id)
    client.user.is_active = True
    client.user.save()
    return HttpResponse(json.dumps({'status':1}))



@login_required(login_url='accounts:login_page')
def get_constituency_by_county(request):
    county_id = request.POST.get('county_id')
    constituency_list = list(Constituency.objects.filter(county=County.objects.get(id=county_id))\
        .values('constituency_name', 'id'))
    return HttpResponse(json.dumps(constituency_list))


@login_required(login_url='accounts:login_page')
def get_ward_by_constituency(request):
    constituency_id = request.POST.get('constituency_id')
    ward_list = list(Ward.objects.filter(constituency=Constituency.objects.get(id=constituency_id))\
                    .values('ward_name', 'id'))
    return HttpResponse(json.dumps(ward_list))


@login_required(login_url='accounts:login_page')
def register_single_aspirant(request):
    password = request.POST.get('password')
    return_data = {}
    if not request.user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        alias_name = request.POST.get('alias_name')
        sms = SMS()
        phone_number = sms.format_phone_number(request.POST.get('phone_number'))
        seat = Seat.objects.get(id=request.POST.get('seat'))
        region_name = request.POST.get('region_name')
        county_id = request.POST.get('county_id')
        constituency_id = request.POST.get('constituency_id')
        ward_id = request.POST.get('ward_id')

        try:
            user_create = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=email,
                email=email,
                is_superuser=False,
                is_staff=True,
                date_joined=datetime.datetime.now()
            )

            aspirant_reg = {
                'full_name': '{} {}'.format(first_name, last_name)
            }

            return_data['MESSAGE'] = []

            return_data['STATUS'] = '1'
            return_data['MESSAGE']. append({
                'STATUS': '1',
                'MESSAGE': 'Client has been registered as system user'
            })

            aspirant = Client()
            aspirant.alias_name = alias_name
            aspirant.phone_number = phone_number
            aspirant.user = User.objects.get(username=email)
            aspirant.seat = seat
            aspirant.region_name = region_name
            aspirant.country = Country.objects.get(country_name='Kenya')
            aspirant.county = County.objects.get(id=county_id)

            if len(constituency_id) > 0 and constituency_id != 'NULL':
                aspirant.constituency = Constituency.objects.get(id=constituency_id)
            if len(ward_id) > 0 and ward_id != 'NULL':
                aspirant.ward = Ward.objects.get(id=ward_id)

            try:
                aspirant.save()
                return_data['MESSAGE'].append({
                    'STATUS': '1',
                    'MESSAGE': 'Client has been registered as a system admin for {}'.format(region_name)
                })

                try:
                    recipient = [user_create]
                    email = SendEmail()
                    txt_template = 'email/email_temlate_aspirant_registration.txt'
                    print ("0000000")
                    html_template = 'email/email_template_aspirant_registration.html'
                    print ("11111111")
                    send_mail = email.send_email(recipient, request, txt_template, html_template)
                    print ("222222222")
                    if send_mail[0]['STATUS'] == '1':
                        return_data['MESSAGE'].append({
                            'STATUS': '1',
                            'MESSAGE': 'An email has been sent to the client'
                        })
                    else:
                        print ("*****")
                        print (send_mail)
                        return_data['MESSAGE'].append({
                            'STATUS': '0',
                            'MESSAGE': 'Email delivery to client failed permanently'
                        })
                except Exception, exp:
                    print(str(exp))
                    return_data['MESSAGE'].append({
                        'STATUS': '0',
                        'MESSAGE': 'Email delivery to client failed permanently'
                    })
            except:
                return_data['MESSAGE'].append({
                    'STATUS': '0',
                    'MESSAGE': 'Client has not been registered as a system admin for {}'.format(region_name)
                })

        except:
            return_data['MESSAGE'].append({
                'STATUS': '0',
                'MESSAGE': 'Client was not registered'
            })

    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def list_of_aspirants(request, offset=0):
    limit = 50
    offset = int(offset)
    next_offset = 0
    prev_offset = offset - limit

    template = 'site_admin/list_of_clients.html'
    try:
        obj_list = Client.objects.all()

        if prev_offset < 0:
            prev_offset = 0

        next_offset = (offset + limit)
        if next_offset > len(obj_list):
            next_offset = offset
    except:
        pass
    context = {
        'client_list': obj_list[offset: offset + limit],
        'current_offset': offset,
        'prev_offset': prev_offset,
        'next_offset': next_offset
    }
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def list_of_volunteers(request, offset=0):
    limit = 50
    offset = int(offset)

    obj_list = Volunteer.objects.all()
    prev_offset = offset - limit

    if prev_offset < 0:
        prev_offset = 0

    next_offset = (offset + limit)
    if next_offset > len(obj_list):
        next_offset = offset

    template = 'site_admin/list_of_volunteers.html'

    context = {
        'volunteer_list': obj_list[offset: offset + limit],
        'current_offset': offset,
        'prev_offset': prev_offset,
        'next_offset': next_offset
    }
    return render(request, template, context)


def flutterwave_response(request):
    data = request.body
    result = json.loads(data)

    try:
        with open('flutterwave_resulturl_post_file.txt', 'a') as post_file:
            post_file.write(str(data))
            post_file.write("\n")
            post_file.write(str(type(data)))
            post_file.write("\n")


    except Exception as e:
        print e


    try:

        with open('flutterwave_resulturl_post_file2.txt', 'a') as post_file:
            post_file.write(result)
            post_file.write("\n")
            post_file.write(str(type(result)))
            post_file.write("\n")
            post_file.write(str(result))
            post_file.write("\n")
    except Exception as e:
        print e

    print result

    print data

    return HttpResponse("ok")





