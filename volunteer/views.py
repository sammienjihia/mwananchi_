import json
import xlwt
from django.shortcuts import render, reverse
from .tokens import shareable_link_token

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib import messages
from django.utils.html import format_html
from django.views.generic.edit import FormView

from client.models import Client
from subscribers.models import Subscriber
from volunteer.models import Volunteer
from .forms import VolunteerForm
from region.models import Country

from app_utility.sms_utils import SMS
from app_utility.email_utils import SendEmail
from app_utility import twitter_utils

# Create your views here.


def index(request):
    pass


@login_required(login_url='accounts:login_page')
def get_landing_page_data(request):
    return_data = {
        'num_of_subscribers': Subscriber.objects.filter(volunteer=Volunteer.objects
                                                        .get(user=request.user)).count()
    }
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def opt_out_of_subscription(request):
    password = request.POST.get('password')
    user = User.objects.get(id=request.user.id)
    return_data = {}
    if not user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        user.is_active = False
        user.save()
        volunteer = Volunteer.objects.get(user=request.user)
        volunteer.is_active = False
        volunteer.save()
        return_data['STATUS'] = '1'
        return_data['URL'] = '/accounts/login_page'

    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def volunteer_list(request, offset=0):
    title = "Volunteer"
    template = 'volunteer/volunteer_list.html'
    offset = int(offset)
    limit = offset + 50

    prev_offset = offset - 50
    if prev_offset < 0:
        prev_offset = 0

    next_offset = 0

    try:
        if request.user.is_staff is True and request.user.is_superuser is True:
            obj_list = Volunteer.objects.all()
        elif request.user.is_staff is True and request.user.is_superuser is False:
            obj_list = Volunteer.objects.filter(aspirant=Client.objects.get(user=request.user))
        next_offset = (offset + 50)
        if next_offset > len(obj_list):
            next_offset = offset
    except:
        pass

    context = {
        "title": title,
        "prevOffset": prev_offset,
        "nextOffset": next_offset,
        "currentOffset": offset,
        "volunteers": obj_list[offset:limit]
    }
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def download_all_volunteers(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Volunteers.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Subscribers')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['First name', 'Last name', 'Phone number','Email address', 'Region name', 'Date registered']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()

    rows = Volunteer.objects.filter(aspirant=Client.objects.get(user=request.user))

    for i in range(len(rows)):
        ws.write(i + 1, 0, rows[i].user.first_name, font_style)
        ws.write(i + 1, 1, rows[i].user.last_name, font_style)
        ws.write(i + 1, 2, rows[i].phone_number, font_style)
        ws.write(i + 1, 3, rows[i].user.email, font_style)
        ws.write(i + 1, 4, rows[i].region_name, font_style)
        ws.write(i + 1, 5, rows[i].user.date_joined.strftime('%Y-%m-%d'), font_style)
    wb.save(response)
    return response


@login_required(login_url='accounts:login_page')
def get_share_volunteer_link(request):
    template = 'volunteer/volunteer_link.html'
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


class VolunteerShareableLinkView(FormView):
    template_name = "volunteer/volunteer_form.html"
    form_class = VolunteerForm
    success_url = 'accounts/login_page'

    def get_context_data(self, **kwargs):
        context = super(VolunteerShareableLinkView, self).get_context_data(**kwargs)
        saved_args = locals()
        uidb64=self.kwargs['uidb64']
        uid = urlsafe_base64_decode(uidb64)
        aspirant = Client.objects.get(user=User.objects.get(id=uid))
        context['user'] = aspirant
        return context

    @staticmethod
    def validate_phone_number(phone_number,asp):
        if Volunteer.objects.filter(phone_number=phone_number,aspirant=asp):
            return False
        return True

    def post (self,request,uidb64=None, token=None, *arg, **kwargs):
        UserModel = get_user_model()
        form = self.form_class(request.POST)

        assert uidb64 is not None and token is not None  # checked by URLconf
        try:
            uid = urlsafe_base64_decode(uidb64)
            asp = Client.objects.get(user = User.objects.get(id=uid))
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        if user is not None and shareable_link_token.check_token(user, token):
            if form.is_valid():
                phone_number= form.cleaned_data['phone_number']
                first_name=form.cleaned_data['first_name']
                last_name=form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                county=form.cleaned_data['county']
                constituency=form.cleaned_data['constituency']
                ward = form.cleaned_data['ward']
                country = Country.objects.get(country_name='Kenya')
                format_number = SMS()
                phone_number= format_number.format_phone_number(phone_number)
                if self.validate_phone_number(phone_number,asp):
                    new_user = User.objects.create_user(first_name=first_name,last_name=last_name,username=email,password=password,email=email,is_staff=False,is_superuser=False,is_active=True)
                    new_volunteer = Volunteer(phone_number=phone_number, aspirant=asp,user=new_user,country=country,county=county,constituency=constituency,ward=ward,is_active=True)
                    try:
                        new_volunteer.save()
                        messages.success(request, format_html("{}<a id='anchor_redirect' href='{}://{}/{}'>{}</a>{}",
                                                              'Successful volunteer registration.', 'http',
                                                              request.META['HTTP_HOST'], 'login_page', 'Click Here',
                                                              ' to access your account.'))

                        txt_template = 'email/volunteer_registration_email.txt'
                        html_template = 'email/volunteer_registration_email.html'
                        recipient = [new_user]
                        try:
                            email = SendEmail()
                            email.tuma_mail(recipient, txt_template, html_template)
                        except Exception, e:
                            print(str(e))
                        return self.form_valid(form)
                    except Exception,e:
                        new_user.delete()
                        messages.error(request, format_html("<span class='w3-text-red'>{}</span>", 'Unsuccessful volunteer registration.'))
                    return self.render_to_response(self.get_context_data(form=form))
                else:
                    messages.error(request, 'Phone Number exists.Unsuccessful volunteer registration.')
                    return self.form_invalid(form)
            else:
                if len(request.POST.get('password')) < 8 or len(request.POST.get('confirm_password')) < 8:
                    messages.error(request, 'Password too short. It should be at least 8 characters.')
                    return self.form_invalid(form)
                else:
                    messages.error(request, 'The passwords do not match.')
                    return self.form_invalid(form)
        else:
            messages.error(request,'The volunteer link is no longer valid.')
            return self.form_invalid(form)
