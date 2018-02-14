import json
import os
import time
import oauth2 as oauth
import urlparse

from django.shortcuts import render, redirect, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse

from accounts.forms import SetPasswordForm, PasswordResetRequestForm
from django.template import loader
from django.views.generic.edit import FormView
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from accounts.tokens import password_reset_token
from django.contrib import messages


from client.models import Client
from subscribers.models import Subscriber
from volunteer.models import Volunteer

from app_utility.email_utils import SendEmail
from celery_stuff.tasks import task_twitter_mentions, task_initial_twitter_timeline

consumer = oauth.Consumer(settings.TWITTER_TOKEN, settings.TWITTER_SECRET)
client = oauth.Client(consumer)

request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token'
authenticate_url = 'https://api.twitter.com/oauth/authenticate'


def index(request):
    template = 'accounts/login_page.html'
    return render(request, template, {})


def login_page(request):
    template = 'accounts/login_page.html'
    return render(request, template, {})


def login_user(request):
    user_name = request.POST.get("user_name")
    password = request.POST.get("password")
    return_data = {}
    user = User.objects.get(username=user_name)

    if user.is_active is False:
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Account has been locked. Contact admin to unlock.'
    else:
        user = authenticate(username=user_name, password=password)

        if user is not None:
            login(request, user)
            return_data['STATUS'] = '1'
            return_data['URL'] = 'landing_page'
        else:
            return_data['STATUS'] = '0'
            return_data['MESSAGE'] = 'Invalid credentials.'

    return HttpResponse(
        json.dumps(return_data),
        content_type="application/json"
    )



@login_required(login_url='accounts:login_page')
def logout_user(request):
    logout(request)
    return redirect('accounts:login_page')


def check_email_exists(request):
    email_address = request.POST.get('email_address')
    user_count = User.objects.filter(Q(email=email_address) | Q(username=email_address)).count()
    return_data = {}
    if user_count > 0:
        return_data['STATUS'] = '1'
    else:
        return_data['STATUS'] = '0'

    return HttpResponse(json.dumps(return_data))




class PasswordResetView(FormView):
    template_name = "accounts/password_reset.html"
    success_url = '/login_page'
    form_class = SetPasswordForm

    def get_context_data(self, **kwargs):
        context = super(PasswordResetView, self).get_context_data(**kwargs)
        saved_args = locals()
        uidb64=self.kwargs['uidb64']
        uid = urlsafe_base64_decode(uidb64)
        context['user'] = User.objects.get(id=uid)
        return context


    def post(self, request, uidb64=None, token=None, *arg, **kwargs):
        UserModel = get_user_model()
        form = self.form_class(request.POST)
        assert uidb64 is not None and token is not None  # checked by URLconf
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None and password_reset_token.check_token(user, token):
            if form.is_valid():
                new_password = form.cleaned_data['new_password2']
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Account password set')
                return self.form_valid(form)
            else:
                new_password = request.POST.get('new_password2')
                if len(request.POST.get('new_password2')) < 8 or len(request.POST.get('new_password1'))<8:
                    messages.error(request, 'Password too short. It should be at least 8 characters.')
                    return self.form_invalid(form)
                else:
                    messages.error(request, 'The passwords do not match')
                    return self.form_invalid(form)
        else:
            messages.error(request,'The set password link is no longer valid')
            return self.form_invalid(form)



class ResetPasswordRequestView(FormView):
    template_name = "accounts/password_reset_email_template.html"
    success_url = '/login_page'
    form_class = PasswordResetRequestForm

    @staticmethod
    def validate_email_address(email):
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data["email_or_username"]
            try:
                user = User.objects.get(Q(username=data) | Q(email=data))
                txt_template = 'email/password_reset_email.txt'
                html_template = 'email/password_reset_email.html'
                recipient = [user]
                email = SendEmail()
                notify_user = email.send_email(recipient, request, txt_template, html_template)
                if notify_user[0]['STATUS'] == '1':
                    result = self.form_valid(form)
                    messages.success(request, 'Email has been sent to ' + data)
                else:
                    result = self.form_invalid(form)
                    messages.success(request, 'Failed to send email!')
                return result
            except Exception, exp:
                print(str(exp))
                result = self.form_invalid(form)
                messages.error(request, 'This user does not exist in the system.')
                return result
        else:
            messages.error(request, 'Invalid Input')

            return self.form_invalid(form)



@login_required(login_url='accounts:login_page')
def change_password(request):
    current_password = request.POST.get('currentPassword')
    new_password = request.POST.get('newPassword')
    user = request.user
    if user.check_password(current_password):
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        return_data = {
            'STATUS': '1',
            'MESSAGE': 'Password has been changed successfully.'
        }
    else:
        return_data = {
            'STATUS': '0',
            'MESSAGE': 'Wrong password.'
        }
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def landing_page(request):
    template = 'accounts/landing.html'
    context = {}
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def profile_page(request):
    template = 'accounts/profile_page.html'
    context = {}
    if request.user.is_superuser is True and request.user.is_staff is True:
        context['subscriber_count'] = Subscriber.objects.count()
    elif request.user.is_superuser is False and request.user.is_staff is True:
        context['subscriber_count'] = Subscriber.objects.filter(client=Client.objects.get(user=request.user)).count()
        aspirant = Client.objects.get(user=request.user)
        profile_pic = aspirant.profile_picture
        context['client'] = Client.objects.get(user=request.user)
        try:
            context['profile_picture_exist'] = True
            context['profile_picture_url'] = profile_pic.url
        except:
            context['profile_picture_exist'] = False
            context['profile_picture_url'] = ''
    elif request.user.is_superuser is False and request.user.is_staff is False:
        context['subscriber_count'] = Subscriber.objects.filter(
            volunteer=Volunteer.objects.get(user=request.user)).count()
        volunteer = Volunteer.objects.get(user=request.user)
        context['county_name'] = volunteer.county.county_name

    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def upload_profile_picture(request):
    uploaded_file = request.FILES['file']
    temp_file_name = uploaded_file.name
    file_content_type = uploaded_file.content_type
    file_extension = file_content_type.split('/')[1]
    file_size = uploaded_file.size
    uploads_dir = 'PROFILE_PICS'
    try:
        os.path.join(settings.MEDIA_ROOT, uploads_dir)
    except:
        pass

    file_name = request.user.username + '_' + str(int(time.time())) + '.' + file_extension
    aspirant = Client.objects.get(user=request.user)
    aspirant.profile_picture.save(file_name, uploaded_file)
    aspirant.save()
    return_data = {
        'STATUS': '1',
        'MESSAGE': 'Profile pic has been updated'
    }
    return HttpResponse(json.dumps(return_data))
    pass


@login_required(login_url='accounts:login_page')
def settings_page(request):
    template = 'accounts/settings_page.html'
    context = {

    }
    if request.user.is_superuser is False and request.user.is_staff is True:
        aspirant = Client.objects.get(user=request.user)
        try:
            if len(aspirant.twitter_oauth_secret) > 5:
                context['twitter_account_set'] = True
            else:
                context['twitter_account_set'] = False
        except:
            context['twitter_account_set'] = False
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def authorize_twitter(request):
    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response from Twitter.")

    request.session['request_token'] = dict(urlparse.parse_qsl(content))

    url = "%s?oauth_token=%s" % (authenticate_url, request.session['request_token']['oauth_token'])

    return HttpResponseRedirect(url)


def twitter_authenticated(request):
    token = oauth.Token(request.session['request_token']['oauth_token'],
                        request.session['request_token']['oauth_token_secret'])
    token.set_verifier(request.GET['oauth_verifier'])
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "GET")
    if resp['status'] != '200':
        print content
        raise Exception("Invalid response from Twitter.")

    access_token = dict(urlparse.parse_qsl(content))

    try:
        tokens = Client.objects.get(twitter_oauth_token=access_token['oauth_token'])
    except:
        profile = Client.objects.get(user=request.user)
        profile.twitter_oauth_token = access_token['oauth_token']
        profile.twitter_oauth_secret = access_token['oauth_token_secret']
        profile.save()
        #task_initial_twitter_timeline.delay(request.user.id)
 	#task_twitter_mentions.delay()

    return redirect('twitter:tweet_search')

@login_required(login_url='accounts:login_page')
def disconnect_twitter_account(request):
    aspirant = Client.objects.get(user=request.user)
    aspirant.twitter_oauth_secret = ''
    aspirant.twitter_oauth_token = ''
    aspirant.twitter_screen_name = ''
    try:
        aspirant.save()
        return_data = {
            'STATUS':'1'
        }
    except:
        return_data = {
            'STATUS': '0'
        }
    return HttpResponse(json.dumps(return_data))







