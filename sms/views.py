import datetime
import json
import os
import time

from django.core.validators import validate_email
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core import serializers


from collections import Counter
from operator import itemgetter

from django.conf import Settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User
from client.models import Client
from sms.models import Inbox, Outbox
from subscribers.models import Subscriber

from app_utility.excel_utils import ExcelFile
from app_utility.sms_utils import SMS
from app_utility import text_analysis
from app_utility.email_utils import SendEmail
from campaign.models import Campaign, CampaignItems, CampaignItemsReception

from pattern.en import sentiment
from survey.models import Survey, SurveyRecipient, SurveyQuestion, SurveyOptions, SurveyResponse
from volunteer.models import Volunteer

from sms.models import SMSMenuLog


from celery_stuff.tasks import task_send_batch_sms_from_excel_upload, task_send_batch_sms_from_recipient_list, task_send_batch_sms_to_all_subscribers

# Create your views here.


def index(request):
    pass


@login_required(login_url='accounts:login_page')
def outbox_list(request, offset=0):
    template = 'sms/outbox_list.html'
    outbox_msgs = Outbox.objects.filter(message_type='CHAT')
    context = {}

    if request.method == 'POST':
        start_date = str(request.POST.get('start_date'))
        end_date = str(request.POST.get('end_date'))
        key_word = str(request.POST.get('key_word'))
        key_word = str(key_word.strip())

        if len(start_date) == 10 and len(end_date) == 10:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            end_date += datetime.timedelta(days=1)
            outbox_msgs = outbox_msgs.filter(
                date_sent__gte=start_date,
                date_sent__lte=end_date)

        elif len(start_date) == 10 and len(end_date) != 10:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            outbox_msgs = outbox_msgs.filter(date_sent__gte=start_date)

        elif len(end_date) == 10 and len(start_date) != 10:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            end_date += datetime.timedelta(days=1)
            outbox_msgs = outbox_msgs.filter(date_sent__lte=end_date)

        if len(key_word) != 0:
            outbox_msgs = outbox_msgs.filter(message__icontains=key_word)
        context["outboxmsgs"] = outbox_msgs

    else:
        offset = int(offset)
        limit = offset + settings.PAGINATION_OFFSET
        prev_offset = offset - settings.PAGINATION_OFFSET

        if prev_offset < 0:
            prev_offset = 0

        next_offset = (offset + settings.PAGINATION_OFFSET)
        if next_offset > len(outbox_msgs):
            next_offset = offset


        context["outboxmsgs"] = outbox_msgs[offset:limit]
        context["prevOffset"] = prev_offset
        context["nextOffset"] = next_offset
        context["currentOffset"] = offset
        context["offsetExist"] = True
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def inbox_list(request, offset=0):
    template = 'sms/inbox_list.html'
    inboxmsgs = Inbox.objects.filter(message_type='CHAT', user=request.user, is_archived=False).order_by('-date_received')
    context = {}
    if request.method == 'POST':
        start_date = str(request.POST.get('start_date'))
        end_date = str(request.POST.get('end_date'))
        sentiment = str(request.POST.get('sentiment'))
        key_word = str(request.POST.get('key_word'))
        key_word = str(key_word.strip())

        if len(start_date) == 10 and len(end_date) == 10:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            end_date += datetime.timedelta(days=1)
            inboxmsgs = inboxmsgs.filter(
                date_received__gte=start_date,
                date_received__lte=end_date
            )

        elif len(start_date) == 10 and len(end_date) != 10:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            inboxmsgs = inboxmsgs.filter(date_received__gte=start_date )

        elif len(end_date) == 10 and len(start_date) != 10:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            end_date += datetime.timedelta(days=1)
            inboxmsgs = inboxmsgs.filter(date_received__lte=end_date)

        if len(key_word) != 0:
            if key_word.isdigit() and len(key_word)>=10:
                sms_util = SMS()
                phone_number = sms_util.format_phone_number(key_word)
                inboxmsgs = inboxmsgs.filter(phone_number=phone_number)
            else:
                inboxmsgs = inboxmsgs.filter(message__icontains=key_word)

        if len(sentiment) != 0:
            inboxmsgs = inboxmsgs.filter(sentiment__icontains=sentiment)

        context["inboxmsgs"] = inboxmsgs
    else:
        offset = int(offset)
        limit = offset + settings.PAGINATION_OFFSET
        prev_offset = offset - settings.PAGINATION_OFFSET

        if prev_offset < 0:
            prev_offset = 0

        next_offset = (offset + settings.PAGINATION_OFFSET)
        if next_offset > len(inboxmsgs):
            next_offset = offset

        print("{} {}".format(offset, limit))
        context["inboxmsgs"] = inboxmsgs[offset:limit]

        context["prevOffset"] = prev_offset
        context["nextOffset"] = next_offset
        context["currentOffset"] = offset
        context["offsetExist"] = True

    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def upload_recipients_excel_file(request):
    uploaded_file = request.FILES['file']
    tep_file_name = uploaded_file.name
    file_content_type = uploaded_file.content_type
    file_extension = file_content_type.split('/')[1]
    file_size = uploaded_file.size
    uploads_dir = 'RECIPIENTS_DIR'

    try:
        os.path.join(settings.MEDIA_ROOT, uploads_dir)
    except:
        pass

    file_name = str(int(time.time()))+'.'+file_extension
    full_file_name = os.path.join(settings.MEDIA_ROOT, uploads_dir, file_name)
    file_save = FileSystemStorage()
    file_save.save(full_file_name, uploaded_file)
    request.session['RECIPIENT_FILE_URL'] = full_file_name

    return_data = {
        'MESSAGE': 'This is awesome',
        'TMP_FILE_NAME': tep_file_name,
        'FILE_NAME': file_name,
        'file_size': file_size,
        'file_content_type': file_content_type
    }

    excel_file = ExcelFile(request.session['RECIPIENT_FILE_URL'])
    headers = excel_file.get_header()
    number_of_recipients = excel_file.get_num_of_records() - 1
    return_data['NUM_OF_RECORDS'] = number_of_recipients
    if headers is None:
        return_data['ERROR'] = 'Invalid file'
        return_data['STATUS'] = '0'
    else:
        return_data['STATUS'] = '1'
        return_data['MESSAGE'] = """You can use the following template names in your message:
            <br>
            {}
            """.format( '['+('], ['.join(headers))+']' )
    return HttpResponse(
        json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def send_batch_sms(request):
    batch_type = request.POST.get('BATCH_TYPE')
    message = request.POST.get('message')

    user_obj = request.user
    user = serializers.serialize('json', [ user_obj, ])

    if batch_type == 'KEYED_NUMBERS' or batch_type == 'SELECT_SUBSCRIBERS':
        sms = SMS()
        recipient_arr = json.loads(request.POST.get('recipientsArr'))
        #sms.send_batch_sms_from_recipient_list(recipient_arr, message, request.user.id)
        task_send_batch_sms_from_recipient_list.delay(recipient_arr, message, user)

    elif batch_type == 'UPLOAD_LIST':
        file_name = request.session['RECIPIENT_FILE_URL']
        sms = SMS()
        #sms.send_batch_sms_from_excel_upload(file_name, message, request.user.id)
        task_send_batch_sms_from_excel_upload.delay(file_name, message, user)
    elif batch_type == 'ALL_SUBSCRIBERS':
        sms = SMS()
        user_id = request.user.id
        subscriber_filter = json.loads(request.POST.get('subscriberFilter'))
        subscriber_filter['user'] = request.user
        subscribers = sms.filter_sms_recipients(subscriber_filter)
        phone_numbers = [subscriber.phone_number for subscriber in subscribers]
        phone_numbers = json.dumps(phone_numbers)
        #sms.send_batch_sms_to_all_subscribers(user_id, phone_numbers, message)
        task_send_batch_sms_to_all_subscribers.delay(user_id, phone_numbers, message)
    elif batch_type == 'VOLUNTEERS':
        sms = SMS()
        user_id = request.user.id
        volunteers = Volunteer.objects.filter(aspirant=Client.objects.get(user=request.user))
        phone_numbers = [volunteer.phone_number for volunteer in volunteers]
        phone_numbers = json.dumps(phone_numbers)
        #sms.send_batch_sms_to_all_subscribers(user_id, phone_numbers, message)
        task_send_batch_sms_to_all_subscribers.delay(user_id, phone_numbers, message)
    else:
        pass

    return HttpResponse(
        json.dumps({
            'MESSAGE': 'Message sent successfully',
            'STATUS': '1'
        }))


@login_required(login_url='accounts:login_page')
def mark_as_read(request):
    message_id = request.POST.get('message_id')
    inbox = Inbox.objects.get(id=message_id)
    inbox.is_received = True
    inbox.save()
    return HttpResponse(json.dumps({
        'STATUS':'1',
        'MESSAGE': inbox.message
    }))


@login_required(login_url='accounts:login_page')
def delete_batch_inbox(request):
    recipients_arr = json.loads(request.POST.get('recipients'))
    for message_id in recipients_arr:
        inbox = Inbox.objects.get(id=message_id)
        inbox.is_archived = True
        inbox.save()
    return HttpResponse(json.dumps({
        'STATUS': '1'
    }))


@login_required(login_url='accounts:login_page')
def reply_batch_inbox(request):
    recipients_arr = json.loads(request.POST.get('recipients'))
    message = request.POST.get('message')
    recipient_list = []
    for message_id in recipients_arr:
        inbox = Inbox.objects.get(id=message_id)
        recipient_list.append(inbox.phone_number)
    recipient_list = list(set(recipient_list))
    # sms_utils = SMS()
    # send_sms = sms_utils.send_batch_sms_to_all_subscribers(request.user.id, json.dumps(recipient_list), message)
    task_send_batch_sms_to_all_subscribers.delay(request.user.id, json.dumps(recipient_list), message)
    status = '1'

    return HttpResponse(json.dumps({
        'STATUS': status
    }))


@login_required(login_url='accounts:login_page')
def reply_to_single_message(request):
    message_id = request.POST.get('message_id')
    message = request.POST.get('message')
    inbox = Inbox.objects.get(id=message_id)
    phone_number = inbox.phone_number
    sms_utils = SMS()
    send_sms = sms_utils.send_single_sms(phone_number, message)
    outbox = Outbox(
        phone_number=phone_number,
        message=message,
        date_sent=datetime.datetime.now()
    )
    outbox.is_sent = True if send_sms else False
    status = '1' if send_sms else '0'
    try:
        outbox.subscriber=Subscriber.objects.get(phone_number__exact=phone_number,
                                                 aspirant=Client.objects.get(user=request.user))
    except:
        pass
    outbox.save()

    return HttpResponse(json.dumps({
        'STATUS': status
    }))


@login_required(login_url='accounts:login_page')
def get_num_of_words(request):
    recipients_arr = json.loads(request.POST.get('recipients'))
    num_of_words = request.POST.get('num_of_words')
    message_arr = []

    for message_id in recipients_arr:
        inbox = Inbox.objects.get(id=message_id)
        message_arr.append(inbox.message)

    frequent_words = text_analysis.word_count(message_arr, num_of_words)
    return HttpResponse(json.dumps(frequent_words))


@login_required(login_url='accounts:login_page')
def inbox_analysis(request):
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    inboxmsgs = Inbox.objects.filter(message_type='CHAT', user=request.user)

    if len(start_date) == 10 and len(end_date) == 10:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        end_date += datetime.timedelta(days=1)
        inboxmsgs = inboxmsgs.filter(
            date_received__gte=start_date,
            date_received__lte=end_date
        )
    elif len(start_date) == 10 and len(end_date) != 10:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        inboxmsgs = inboxmsgs.filter(date_received__gte=start_date)
    elif len(end_date) == 10 and len(start_date) != 10:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        end_date += datetime.timedelta(days=1)
        inboxmsgs = inboxmsgs.filter(date_received__lte=end_date)

    date_list = [obj.date_received.strftime('%d %b %Y') for obj in inboxmsgs]
    date_keys = list(Counter(date_list).keys())
    date_count_values = list(Counter(date_list).values())
    temp_items = []

    for i in range(0, len(date_keys)):
        temp_items.append({
            'date': date_keys[i],
            'num': date_count_values[i]
        })

    return_data = sorted(temp_items, key=itemgetter('date'))
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def get_last_7_day_sms_count(request):
    inbox_list = list(Inbox.objects.filter(user=request.user).order_by('-date_received').values('date_received').distinct())[0:7]

    return_data = []
    for date_obj in inbox_list:
        return_data.append({
            'date': date_obj['date_received'].strftime('%d %b %Y'),
            'num': Inbox.objects.filter(user=request.user, date_received=date_obj['date_received']).count()
        })

    return HttpResponse(json.dumps(return_data))


@csrf_exempt
def receive_sms(request):
    try:
        f = open("log.log", "a+")
        data_to_log = request.POST
        data_to_log['date_time'] = str(datetime.datetime.now())
        f.write("{}\n".format(json.dumps(data_to_log)))
        f.close()
    except:
        pass

    sender = request.POST.get('from') # phone number from which the message originated from
    message = request.POST.get('text') # Message from sender
    message = message.strip()
    date = request.POST.get('date') # Date time when the message was sent
    msg_id = request.POST.get('id') # Message ID from Africa's Talking

    aspirant = Client.objects.all()[0]

    sms_inbox = Inbox(
        africastalking_msg_id=msg_id,
        phone_number=sender,
        message=message,
        date_created=datetime.datetime.now(),
        date_received=date,
        user=aspirant.user)

    subscriber_exist = Subscriber.objects.filter(phone_number=sender).exists()
    volunteer_exist = Volunteer.objects.filter(phone_number=sender).exists()

    try:
        message_arr = message.split(' ')
        first_word = message_arr[0].lower()
        first_word = first_word.strip()
        sms_util = SMS()

        if len(message_arr) == 1:
            if first_word == 'vote' and subscriber_exist is False: # subscriber user
                sms_inbox.message_type = 'SUBSCRIBE'
                sms_inbox.save()
                subscriber = Subscriber(
                    phone_number=sms_util.format_phone_number(sender),
                    aspirant=aspirant,
                    is_active=True)
                subscriber.save()
                ret_msg = """You have successfully subscribe to {}. Send the word campaign to {} to view his campaign."""\
                    .format(aspirant.alias_name, settings.SMS_SHORT_CODE)
                sms_util.send_single_sms(sms_util.format_phone_number(sender), ret_msg)
                Outbox(phone_number=sms_util.format_phone_number(sender),
                       message=ret_msg, message_type="ACK", is_sent=True, user=aspirant.user,
                       date_sent=datetime.datetime.now()).save()
                return

            elif first_word == 'volunteer':
                ret_msg = """To register as {}'s volunteer, send the word volunteer followed by your email address to {}.""" \
                    .format(aspirant.alias_name, settings.SMS_SHORT_CODE)
                sms_util.send_single_sms(sms_util.format_phone_number(sender), ret_msg)
                Outbox(phone_number=sms_util.format_phone_number(sender),
                       message=ret_msg, message_type="ACK", is_sent=True, user=aspirant.user,
                       date_sent=datetime.datetime.now()).save()

            elif first_word.isdigit(): # SMS menu
                phone_number = sms_util.format_phone_number(sender)
                sms_menu_log = SMSMenuLog.objects.filter(phone_number=phone_number).order_by('-date_created')[0]
                allowed_options = json.loads(sms_menu_log.allowed_options)
                extra_info = json.loads(sms_menu_log.extra_info)
                menu_type = sms_menu_log.menu_type
                menu_option = int(first_word)

                if menu_option not in allowed_options:
                    msg = extra_info['FALL_BACK_SMS']
                    sms_util.send_single_sms(phone_number, msg)
                    return

                if menu_type == 'MANIFESTO': #Send campaign
                    sms_inbox.message_type = 'MANIFESTO'
                    sms_inbox.save()

                    manifesto_id = extra_info['MANIFESTO_ID']
                    options_mapping = extra_info['OPTIONS_MAPPING']
                    manifesto = Campaign.objects.get(id=manifesto_id)
                    manifesto_item_id = options_mapping[first_word]
                    manifesto_item = CampaignItems.objects.get(campaign=manifesto, id=manifesto_item_id)
                    manifesto_msg = """{}\n{}""".format(manifesto_item.title, manifesto_item.content)
                    sms_util.send_single_sms(phone_number, manifesto_msg)

                    manifesto_item_reception = CampaignItemsReception(
                        manifesto_item=CampaignItems.objects.get(id=manifesto_item_id),
                        date_read=datetime.datetime.now())

                    try:
                        manifesto_item_reception.subscriber=Subscriber.objects.get(phone_number=phone_number)
                    except:
                        pass
                    manifesto_item_reception.save()

                elif menu_type == 'SURVEY': #Send survey
                    sms_inbox.message_type = 'SURVEY'
                    sms_inbox.save()

                    survey_id = extra_info['SURVEY_ID']
                    was_question = extra_info['WAS_QUESTION']

                    if was_question == 1:  # Save survey response
                        options_mapping = extra_info['OPTIONS_MAPPING']
                        survey_response = SurveyResponse()
                        survey_response.survey_option = SurveyOptions.objects.get(id=options_mapping[first_word])
                        try:
                            survey_response.subscriber = Subscriber.objects.get(phone_number=sms_util.format_phone_number(phone_number))
                        except:
                            pass
                        survey_response.save()

                    next_question_number = extra_info['NEXT_QUESTION_NUMBER']
                    survey = Survey.objects.get(id=survey_id)

                    try:
                        survey_question = SurveyQuestion.objects.get(survey=survey, question_number=next_question_number)
                        question_options = SurveyOptions.objects.filter(survey_question=survey_question)
                        msg = "{}\n".format(survey_question.question)
                        fall_back_sms = "Invalid option.\n"
                        allowed_options = []
                        options_mapping = {}

                        for i in range(0, len(question_options)):
                            msg += "{}. {}\n".format(i+1, question_options[i].option)
                            fall_back_sms += "{}. {}\n".format(i+1, question_options[i].option)
                            allowed_options.append(i+1)
                            options_mapping[i + 1] = question_options[i].id

                        SMSMenuLog(
                            date_created=datetime.datetime.now(),
                            phone_number=phone_number,
                            menu_type='SURVEY',
                            allowed_options=json.dumps(allowed_options),
                            extra_info=json.dumps({
                                'WAS_QUESTION': 1,
                                'NEXT_QUESTION_NUMBER': next_question_number + 1,
                                'SURVEY_ID': survey_id,
                                'FALL_BACK_SMS': fall_back_sms,
                                'OPTIONS_MAPPING': options_mapping})).save()
                        sms_util.send_single_sms(phone_number, msg)
                    except:
                        msg = "Thank you for participating in this survey."
                        sms_util.send_single_sms(phone_number, msg)

        elif first_word == 'volunteer' and volunteer_exist is False:  # Register volunteer
            sms_inbox.message_type = 'VOLUNTEER'
            sms_inbox.save()
            email_address = message_arr[1]

            try:
                validate_email(email_address)
                user = User(username=email_address, email=email_address)
                user.save()
                volunteer = Volunteer(
                    phone_number=sms_util.format_phone_number(sender),
                    aspirant=aspirant,
                    is_active=True,
                    user=user)
                volunteer.save()
                try:
                    recipient = [user]
                    email = SendEmail()
                    txt_template = 'email/email_template_volunteer_registration.txt'
                    html_template = 'email/email_template_volunteer_registration.html'
                    send_mail = email.tuma_mail(recipient, txt_template, html_template)
                    if send_mail:
                        ret_msg = """You have successfully been registered as {}'s volunteer. A verification link has been sent to {}.""" \
                            .format(aspirant.alias_name, email_address)
                    else:
                        ret_msg = """Unsuccessful registration.Unable to sent verification link to {}""" \
                            .format(email_address)
                        volunteer.delete()
                        user.delete()
                except Exception, e:
                    ret_msg = """Unsuccessful registration.Unable to sent verification link to {}""" \
                        .format(email_address)
                    volunteer.delete()
                    user.delete()
                sms_util.send_single_sms(sms_util.format_phone_number(sender), ret_msg)
                Outbox(phone_number=sms_util.format_phone_number(sender),
                       message=ret_msg, message_type="ACK", is_sent=True, user=aspirant.user,
                       date_sent=datetime.datetime.now()).save()
                return

            except:
                ret_msg = """Invalid email address.Please send the word volunteer followed by a valid email address to {}.""" \
                    .format(aspirant.alias_name, settings.SMS_SHORT_CODE)
                sms_util.send_single_sms(sms_util.format_phone_number(sender), ret_msg)
                Outbox(phone_number=sms_util.format_phone_number(sender), user=aspirant.user,
                       message=ret_msg, message_type="ACK", is_sent=True,
                       date_sent=datetime.datetime.now()).save()

        else:
            polarity_subjectivity = sentiment(message)
            sms_inbox.polarity = polarity_subjectivity[0]
            sms_inbox.subjectivity = polarity_subjectivity[1]
            if polarity_subjectivity[1] > 0:
                if polarity_subjectivity[0] >= 0.1:
                    sms_inbox.sentiment = 'POSITIVE'
                else:
                    sms_inbox.sentiment = 'NEGATIVE'
            else:
                sms_inbox.sentiment = 'NEUTRAL'
            sms_inbox.message_type = 'CHAT'
            sms_inbox.save()

    except Exception, exp:
        print ("{} sending sms.".format(exp))


@login_required(login_url='accounts:login_page')
def get_sentiment_analysis(request):
    positive,negative,neutral = 0,0,0
    recipients_arr = json.loads(request.POST.get('recipients'))

    messages = Inbox.objects.filter(pk__in = recipients_arr)
    for message in messages:
        if message.sentiment == 'POSITIVE':
            positive += 1
        elif message.sentiment == 'NEGATIVE':
            negative += 1
        else:
            neutral += 1
    return_data = {
        'positive' : positive,
        'negative' : negative,
        'neutral' : neutral,
    }
    return HttpResponse(json.dumps(return_data))




