import datetime
import json
import os
import xlwt
import time

from collections import Counter
from operator import itemgetter

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Count
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render, reverse
from django.utils.timezone import now
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.html import format_html
from django.views.generic.edit import FormView

from app_utility.excel_utils import ExcelFile
from app_utility.sms_utils import SMS
from app_utility import twitter_utils

from client.models import Client
from language.models import Language
from subscribers.models import Subscriber
from region.models import Country, County, Constituency, Ward
from volunteer.models import Volunteer

from subscribers.forms import SubscriberForm
from subscribers.tokens import shareable_link_token


# Create your views here.


def index(request):
    pass


@login_required(login_url='accounts:login_page')
def get_number_of_subscribers(request):
    subscriber_count = Subscriber.objects.filter(client=Client.objects.get(user=request.user)).count()
    return_data = {
        'NUM_OF_SUBSCRIBERS': subscriber_count
    }
    if subscriber_count > 0:
        return_data['STATUS'] = '1'
    else:
        return_data['STATUS'] = '0'
    counties = County.objects.all().values('id', 'county_name')
    return_data['counties'] = list(counties)
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def get_subscribers_count_on_filter(request):

    def date_range(min_age, max_age):
        min_age = int(min_age)
        max_age = int(max_age)
        current = now().date()
        min_date = datetime.date(current.year - min_age, current.month, current.day)
        max_date = datetime.date(current.year - max_age, current.month, current.day)
        return min_date, max_date

    min_age = request.POST.get('min_age')
    max_age = request.POST.get('max_age')

    if len(min_age) == 0:
        min_age = 18

    if len(max_age) == 0:
        max_age = 116

    gender = request.POST.get('gender')

    if len(request.POST.get('county_id')) > 0 and request.POST.get('county_id') != 'NULL':
        county_id = int(request.POST.get('county_id'))
    else:
        county_id =None

    if len(request.POST.get('constituency_id')) > 0 and request.POST.get('constituency_id') != 'NULL':
        constituency_id = int(request.POST.get('constituency_id'))
    else:
        constituency_id = None

    if len(request.POST.get('ward_id')) > 0 and request.POST.get('ward_id') != 'NULL':
        ward_id = int(request.POST.get('ward_id'))
    else:
        ward_id = None

    date_range = date_range(min_age, max_age)

    if gender == 'NULL' or len(gender) == 0:
        gender = None

    filters = {
        'gender': gender,
        'county_id': county_id,
        'constituency_id': constituency_id,
        'ward_id': ward_id
    }

    subscribers = Subscriber.objects.filter(
        date_of_birth__gte=date_range[1],
        date_of_birth__lte=date_range[0], client= Client.objects.get(user=request.user)).all()

    for key, value in filters.items():
        if value is not None:
            subscribers = subscribers.filter(**{key: value})

    try:
        return_data = {
            'NUM_OF_SUBSCRIBERS': subscribers.count()
        }
    except:
        return_data = {
            'NUM_OF_SUBSCRIBERS': 0
        }

    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def get_subscribers_list_for_sms(request):
    subscribers_list = Subscriber.objects.filter(client=Client.objects.get(user=request.user))\
        .values_list('id', 'first_name', 'last_name', 'phone_number')
    return_data = []
    for obj in subscribers_list:
        obj = list(obj)
        return_data.append({
            'id': obj[0],
            'fullName': obj[1] + ' ' + obj[2],
            'mobileNumber': obj[3]
        })
    return HttpResponse(
        json.dumps(return_data)
    )


@login_required(login_url='accounts:login_page')
def batch_upload_subscribers_form(request):
    template = 'subscribers/batch_upload_subscribers_form.html'
    context = {}
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def upload_subscribers_file(request):
    uploaded_file = request.FILES['file']
    tep_file_name = uploaded_file.name
    file_content_type = uploaded_file.content_type
    file_extension = file_content_type.split('/')[1]
    file_size = uploaded_file.size
    uploads_dir = 'SUBSCRIBERS_DIR'

    try:
        os.path.join(settings.MEDIA_ROOT, uploads_dir)
    except:
        pass

    file_name = str(int(time.time())) + '.' + file_extension
    full_file_name = os.path.join(settings.MEDIA_ROOT, uploads_dir, file_name)
    file_save = FileSystemStorage()
    file_save.save(full_file_name, uploaded_file)
    request.session['SUBSCRIBERS_FILE_URL'] = full_file_name

    return_data = {
        'TMP_FILE_NAME': tep_file_name,
        'FILE_NAME': file_name,
        'file_size': file_size,
        'file_content_type': file_content_type
    }

    excel_file = ExcelFile(request.session['SUBSCRIBERS_FILE_URL'])
    headers = excel_file.get_header()

    allowed_headers = ['First name',
        'Last name',
        'Mobile number',
        'Email address'
        'Country',
        'Date of birth',
        'Gender',
        'County',
        'Constituency',
        'Ward'
    ]

    return_data['NUM_OF_RECORDS'] = excel_file.get_num_of_records() - 1
    return_data['HEADER'] = headers

    if headers == allowed_headers:
        return_data['ERROR'] = 'Invalid file'
        return_data['STATUS'] = '0'
    else:
        return_data['STATUS'] = '1'
        records = excel_file.get_records(True)
        return_data['SUBSCRIBERS_LIST'] = []
        for record in records:
            record = list(record)
            return_data['SUBSCRIBERS_LIST'].append({
                'firstName': record[0],
                'lastName': record[1],
                'mobileNumber': record[2],
                'emailAddress': record[3],
                'country': record[4],
                'dateOfBirth': record[5].strftime('%d %b %Y'),
                'gender': record[6],
                'county': record[7],
                'constituency': record[8],
                'ward': record[9]
            })
    return HttpResponse(
        json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def batch_approve_subscribers_from_file(request):
    password = request.POST.get('password')
    user = User.objects.get(id=request.user.id)

    return_data = {}
    if not user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        excel_file = ExcelFile(request.session['SUBSCRIBERS_FILE_URL'])
        records = excel_file.get_records(True)
        num_of_records = len(records)
        i = 0
        return_data['MESSAGE'] = []
        for record in records:
            try:
                record = list(record)
                subscriber = Subscriber()
                subscriber.first_name = record[0]
                subscriber.last_name = record[1]
                sms_utility = SMS()
                subscriber.phone_number = sms_utility.format_phone_number(record[2])
                subscriber.email_address = record[3]
                subscriber.country = Country.objects.get(country_name='Kenya')
                subscriber.gender = record[6]

                if request.user.is_staff is True and request.user.is_superuser is False:
                    subscriber.aspirant = Client.objects.get(user=request.user)
                elif request.user.is_staff is False and request.user.is_superuser is False:
                    subscriber.aspirant = Volunteer.objects.get(user = request.user).aspirant
                    subscriber.volunteer = Volunteer.objects.get(user=request.user)

                if len(record[7]) > 0:
                    subscriber.county = County.objects.get(county_name=record[7])
                if len(record[8]) > 0:
                    subscriber.constituency = Constituency.objects.get(constituency_name=record[8])
                if len(record[9]) > 0:
                    subscriber.ward = Ward.objects.get(ward_name=record[9])

                try:
                    subscriber.date_of_birth = record[5]
                    get_age = lambda dob: datetime.datetime.today().year - dob.year \
                        - ((datetime.datetime.today().month, datetime.datetime.today().day) \
                            < (dob.month, dob.day))
                    subscriber.current_age = get_age(record[5])
                except:
                    pass

                subscriber.date = datetime.datetime.now()
                subscriber.is_active = True
                subscriber.save()
                i += 1
                return_data['MESSAGE'].append({
                    'STATUS': '1',
                    'MESSAGE': '{} {} has been registered successfully'.format(record[0], record[1])
                })
            except Exception as exp:
                print('Errorr while registering {}'.format(exp))
                return_data['MESSAGE'].append({
                    'STATUS': '0',
                    'MESSAGE': '{} {} has not been registered'.format(record[0], record[1])
                })
        return_data['STATUS'] = '1'
        return_data['FINAL_MSG'] = '{} subscribers have been uploaded'.format(i)

    return HttpResponse(
        json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def single_upload_subscribers_form(request):
    template = 'subscribers/single_upload_subscribers_form.html'
    context = {
        'county_list': County.objects.all(),
        'language_list': Language.objects.all()
    }
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def register_single_subscriber(request):
    password = request.POST.get('password')
    return_data = {}
    if not request.user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        date_of_birth = request.POST.get('date_of_birth')
        phone_number = request.POST.get('phone_number')
        phone_number = phone_number.replace(' ', '')
        gender = request.POST.get('gender')
        language_id = request.POST.get('language_id')
        county_id = request.POST.get('county_id')
        constituency_id = request.POST.get('constituency_id')
        ward_id = request.POST.get('ward_id')

        subscriber = Subscriber()
        subscriber.first_name = first_name
        subscriber.last_name = last_name
        subscriber.email_address = email
        subscriber.date_of_birth = datetime.datetime.strptime(date_of_birth, '%Y-%m-%d')
        sms = SMS()
        subscriber.phone_number = sms.format_phone_number(phone_number)
        subscriber.gender = gender
        subscriber.language  =Language.objects.get(id=language_id)
        subscriber.county = County.objects.get(id=county_id)

        if constituency_id.isdigit():
            subscriber.constituency = Constituency.objects.get(id=constituency_id)
        if ward_id.isdigit():
            subscriber.ward = Ward.objects.get(id=ward_id)

        subscriber.is_active = True
        subscriber.aspirant = Volunteer.objects.get(user=request.user).aspirant
        subscriber.volunteer = Volunteer.objects.get(user=request.user)
        subscriber.date = datetime.datetime.now()


        try:
            subscriber.save()
            return_data['STATUS'] = '1'
            return_data['MESSAGE'] =  'Subscriber has been registered on the system'
        except Exception, exp:
            return_data['STATUS'] = '0'
            return_data['MESSAGE'] = 'Subscriber failed to be registered {}'.format(str(exp))
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def subscribers_list(request, offset=0):
    title = "Subscribers"
    template = 'subscribers/subscribers_list.html'
    offset = int(offset)
    limit = offset + settings.PAGINATION_OFFSET

    prev_offset = offset - settings.PAGINATION_OFFSET
    if prev_offset < 0:
        prev_offset = 0

    next_offset = 0

    try:
        if request.user.is_staff is True and request.user.is_superuser is True:
            obj_list = Subscriber.objects.all()
        elif request.user.is_staff is True and request.user.is_superuser is False:
            obj_list = Subscriber.objects.filter(client=Client.objects.get(user=request.user))
        elif request.user.is_staff is False and request.user.is_superuser is False:
            obj_list = Subscriber.objects.filter(volunteer=Volunteer.objects.get(user=request.user))
        next_offset = (offset + settings.PAGINATION_OFFSET)
        if next_offset > len(obj_list):
            next_offset = offset
    except:
        pass

    context = {
        "title": title,
        "prevOffset": prev_offset,
        "nextOffset": next_offset,
        "currentOffset": offset,
        "subscribers": obj_list[offset:limit]
    }
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def subscriber_analysis_by_gender(request):
    subscribers = Subscriber.objects\
        .values('gender')\
        .annotate(num=Count('gender')).exclude(gender__isnull=True)

    if request.user.is_staff is True and request.user.is_superuser is False:
        subscribers = subscribers.filter(client=Client.objects.get(user=request.user))

    elif request.user.is_staff is False and request.user.is_superuser is False:
        subscribers = subscribers.filter(volunteer=Volunteer.objects.get(user=request.user))

    return_data = []
    for obj in subscribers:
        return_data.append({
            'gender': obj['gender'],
            'num': obj['num']
        })
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def subscriber_analysis_by_age(request):
    subscribers = Subscriber.objects\
        .values('date_of_birth').exclude(date_of_birth__isnull=True)
    if request.user.is_staff is True and request.user.is_superuser is False:
        subscribers = subscribers.filter(client=Client.objects.get(user=request.user))
    elif request.user.is_staff is False and request.user.is_superuser is False:
        subscribers = subscribers.filter(volunteer=Volunteer.objects.get(user=request.user))

    age_arr = []

    def get_age(dob):
        age = datetime.datetime.today().year - dob.year\
            - ((datetime.datetime.today().month, datetime.datetime.today().day)\
                < (dob.month, dob.day))
        return age

    try:
        for subscriber in subscribers:
            age_arr.append(get_age(subscriber['date_of_birth']))
    except:
        pass

    age_keys = list(Counter(age_arr).keys())
    age_count_values = list(Counter(age_arr).values())
    temp_items = []
    print(age_keys)
    for i in range(0, len(age_keys)):
        temp_items.append({
            'age': age_keys[i],
            'num': age_count_values[i]
        })

    return_data = sorted(temp_items, key=itemgetter('age'))
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def subscriber_analysis_by_county(request):
    subscribers = Subscriber.objects\
        .values('county') \
        .annotate(num=Count('county')).exclude(county__isnull=True)

    if request.user.is_staff is True and request.user.is_superuser is False:
        subscribers = subscribers.filter(client=Client.objects.get(user=request.user))
    elif request.user.is_staff is False and request.user.is_superuser is False:
        subscribers = subscribers.filter(volunteer=Volunteer.objects.get(user=request.user))

    return_data = []
    for obj in subscribers:
        county = County.objects.get(id=obj['county'])
        return_data.append({
            'countyName': county.county_name,
            'num': obj['num']
        })
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def subscriber_analysis_by_ward(request):
    subscribers = Subscriber.objects \
        .values('ward')\
        .annotate(num=Count('ward')).exclude(ward__isnull=True)

    if request.user.is_staff is True and request.user.is_superuser is False:
        subscribers = subscribers.filter(client=Client.objects.get(user=request.user))
    elif request.user.is_staff is False and request.user.is_superuser is False:
        subscribers = subscribers.filter(volunteer=Volunteer.objects.get(user=request.user))
    return_data = []
    for obj in subscribers:
        try:
            ward = Ward.objects.get(id=obj['ward'])
            return_data.append({
                'wardName': ward.ward_name,
                'num': obj['num']
            })
        except:
            pass
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def download_all_subscribers(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Subscribers.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Subscribers')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['First name', 'Last name', 'Gender', 'Date of birth',
               'Phone number', 'Email address', 'Date registered']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    rows = Subscriber.objects.filter(client=Client.objects.get(user=request.user))
    print(rows)
    for i in range(len(rows)):
        ws.write(i + 1, 0, rows[i].first_name, font_style)
        ws.write(i + 1, 1, rows[i].last_name, font_style)
        ws.write(i + 1, 2, rows[i].gender, font_style)
        ws.write(i + 1, 3, rows[i].date_of_birth.strftime('%Y-%m-%d'), font_style)
        ws.write(i + 1, 4, rows[i].phone_number, font_style)
        ws.write(i + 1, 5, rows[i].email_address, font_style)
        ws.write(i + 1, 6, rows[i].date.strftime('%Y-%m-%d'), font_style)
    wb.save(response)
    return response


@login_required(login_url='accounts:login_page')
def get_share_subscription_link(request):
    template = 'subscribers/subscribers_link.html'
    user = User.objects.get(username=request.user.username)
    dict_obj = model_to_dict(user,fields=['id'])
    context={'domain':request.META['HTTP_HOST'],'uid':urlsafe_base64_encode(force_bytes(dict_obj['id'])),'token': shareable_link_token.make_token(user),'protocol': 'http'}
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def share_link_on_twitter(request):
    link = request.POST.get('link')
    message = format_html('<a href="{}">Click here.</a>', link)
    aspirant = Client.objects.get(user=request.user)
    post_tweet = twitter_utils.post_sth_to_twitter(message, aspirant)
    return_data = {}
    if post_tweet:
        return_data['STATUS'] = '1'
    else:
        return_data['STATUS'] = '0'
    return HttpResponse(json.dumps(return_data))


class SubscribeShareableLinkView(FormView):
    template_name = "subscribers/subscribers_form.html"
    form_class = SubscriberForm
    success_url = 'subscribe_to_aspirant/'

    def get_success_url(self):
        return reverse('volunteer_link',kwargs={'token':self.kwargs['token'],'uidb64':self.kwargs['uidb64']})

    def get_context_data(self, **kwargs):
        context = super(SubscribeShareableLinkView, self).get_context_data(**kwargs)
        saved_args = locals()
        uidb64=self.kwargs['uidb64']
        uid = urlsafe_base64_decode(uidb64)
        aspirant = Client.objects.get(user=User.objects.get(id=uid))
        context['user'] = aspirant
        return context

    @staticmethod
    def validate_phone_number(phone_number,user):
        if Subscriber.objects.filter(phone_number=phone_number,client=user):
            return False
        return True

    def post (self,request,uidb64=None, token=None, *arg, **kwargs):
        UserModel = get_user_model()
        form = self.form_class(request.POST)

        assert uidb64 is not None and token is not None  # checked by URLconf
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = Client.objects.get(user = User.objects.get(id=uid))
            u = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        if user is not None and shareable_link_token.check_token(u, token):
            if form.is_valid():
                phone_number= form.cleaned_data['phone_number']
                first_name=form.cleaned_data['first_name']
                last_name=form.cleaned_data['last_name']
                gender = form.cleaned_data['gender']
                date_of_birth = form.cleaned_data['date_of_birth']
                email_address = form.cleaned_data['email_address']
                language = form.cleaned_data['language']
                country=Country.objects.get(country_name='Kenya')
                county=form.cleaned_data['county']
                constituency=form.cleaned_data['constituency']
                ward = form.cleaned_data['ward']
                format_number = SMS()
                phone_number= format_number.format_phone_number(phone_number)
                if self.validate_phone_number(phone_number,user) is True:
                    asp = Client.objects.get(user = User.objects.get(id=uid))
                    new_subscriber = Subscriber(first_name=first_name,
                                                last_name=last_name,
                                                gender=gender,
                                                date_of_birth=date_of_birth,
                                                email_address=email_address,
                                                language=language,
                                                is_active=True,
                                                phone_number=phone_number,
                                                client=asp,
                                                country=country,county=county,
                                                constituency=constituency,ward=ward)
                    new_subscriber.save()
                    messages.success(request, 'Successful subscription.')
                    return self.render_to_response(self.get_context_data(form=form))
                else:
                    messages.error(request, 'Unsuccessful subscription.You are already subscribed to this client.')
                    return self.form_invalid(form)
            else:
                messages.error(request, 'Unsuccessful subscription.')
                return self.form_invalid(form)
        else:
            messages.error(request,'The subscription link is no longer valid.')
            return self.form_invalid(form)





