import datetime
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from client.models import Client
from subscribers.models import Subscriber
from region.models import Country, County, Constituency
from survey.models import Survey, SurveyRecipient, SurveyOptions, SurveyQuestion, SurveyResponse

from app_utility.sms_utils import SMS as SmsUtil
from sms.models import SMSMenuLog

# Create your views here.


@login_required(login_url='accounts:login_page')
def index(request):
    pass


@login_required(login_url='accounts:login_page')
def new_survey_form(request):
    template = 'survey/new_survey_form.html'
    context = {
        'county_list': County.objects.all(),
        'num_of_subscribers': Subscriber.objects.filter(client=Client.objects.get(user=request.user)).count()
    }
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def publish_new_survey(request):
    password = request.POST.get('password')
    return_data = {}
    if not request.user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        survey_title = request.POST.get('surveyTitle')
        survey_description = request.POST.get('surveyDescription')
        survey_content = json.loads(request.POST.get('surveyContent'))
        survey = Survey()
        survey.survey_title = survey_title
        survey.survey_desc = survey_description
        survey.aspirant = Client.objects.get(user=request.user)
        return_data['MESSAGE'] = []
        try:
            survey.save()
            return_data['MESSAGE'].append({
                'STATUS': '1',
                'MESSAGE': 'Survey has been created.'
            })
            for content in survey_content:
                survey_question = SurveyQuestion()
                survey_question.survey = survey
                survey_question.question_number = content['question_number']
                survey_question.question = content['question']
                try:
                    survey_question.save()
                    return_data['MESSAGE'].append({
                        'STATUS': '1',
                        'MESSAGE': "'{}' survey question has been added.".format(content['question'])
                    })
                    options_list = content['option'].split('#')

                    for option in options_list:
                        try:
                            survey_options = SurveyOptions()
                            survey_options.option = option
                            survey_options.survey_question = survey_question
                            survey_options.save()
                            return_data['MESSAGE'].append({
                                'STATUS': '1',
                                'MESSAGE': "'{}' survey option has been added.".format(option)
                            })
                        except Exception as ex:
                            return_data['MESSAGE'].append({
                                'STATUS': '0',
                                'MESSAGE': "'{}' survey option failed to be added. Error: {}".format(option, str(ex))
                            })
                except Exception as ex:
                    return_data['MESSAGE'].append({
                        'STATUS': '0',
                        'MESSAGE': "'{}' survey question failed to be added. Error: ".format(content['question'], str(ex))
                    })
            subscriber_filter = json.loads(request.POST.get('subscriber_filter'))
            subscriber_filter['user'] = request.user
            try:
                sms_utils = SmsUtil()
                subscribers = sms_utils.filter_sms_recipients(subscriber_filter)
                for subscriber in subscribers:
                    survey_recipient = SurveyRecipient(
                        survey=survey,
                        subscriber=subscriber)
                    survey_recipient.save()
            except Exception as exe:
                print(str(exe))
                pass
        except Exception as ex:
            return_data['MESSAGE'].append({
                'STATUS': '0',
                'MESSAGE': 'Survey failed to be created. Error: '.format(str(ex))
            })

    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def survey_listing_page(request):
    template = 'survey/survey_listing_page.html'
    context = {}
    try:
        survey_list = Survey.objects.filter(client=Client.objects.get(user=request.user)).order_by('-id')
        context['survey_list'] = []
        for survey in survey_list:
            questions_list = SurveyQuestion.objects.filter(survey=survey).order_by('id')
            questions_obj = []
            for question in questions_list:
                options = SurveyOptions.objects.filter(survey_question=question).order_by('id')
                options_dic = options.values()
                for i in range(0, len(options_dic)):
                    try:
                        options_dic[i]['response_count'] = SurveyResponse.objects.filter(survey_option=options[i]).count()
                    except Exception, e:
                        print(str(e))
                        options_dic[i]['response_count'] = 0
                        pass

                questions_obj.append({
                    'question': question.question,
                    'options': options_dic
                })
            context['survey_list'].append({
                'survey_title': survey.survey_title,
                'survey_id': survey.id,
                'survey_desc': survey.survey_desc,
                'questions_obj': questions_obj
            })
    except:
        pass
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def delete_survey(request):
    password = request.POST.get('password')
    return_data = {}

    if not request.user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        survey_id = request.POST.get('survey_id')
        try:
            survey = Survey.objects.get(id=survey_id)
            survey_questions = SurveyQuestion.objects.filter(survey=survey)
            for question in survey_questions:
                SurveyOptions.objects.filter(survey_question=question).delete()
            survey_questions.delete()
            SurveyRecipient.objects.filter(survey=survey).delete()
            survey.delete()
            return_data['STATUS'] = '1'
            return_data['MESSAGE'] = 'Survey has been deleted'
        except:
            return_data['STATUS'] = '0'
            return_data['MESSAGE'] = 'Error while deleting survey'
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def broadcast_survey(request):
    password = request.POST.get('password')
    return_data = {}
    if not request.user.check_password(password):
        return_data['STATUS'] = '0'
        return_data['MESSAGE'] = 'Wrong password'
    else:
        survey_id = request.POST.get('survey_id')
        survey = Survey.objects.get(id=survey_id)
        survey_recipients = SurveyRecipient.objects.filter(survey=survey)
        sms_util = SmsUtil()
        shortcode = 1234
        try:
            for recipient in survey_recipients:
                subscriber = recipient.subscriber
                phone_number = sms_util.format_phone_number(subscriber.phone_number)
                try:
                    if len(subscriber.first_name) > 0:
                        msg = """{}, {} is requesting that you participate in this survey. To participate in this survey, send 1 to {}""".format(
                            subscriber.first_name, subscriber.aspirant.alias_name, shortcode)
                except:
                    msg = """Dear subscriber, {} is requesting that you participate in this survey. To participate in this survey, send 1 to {}""".format(
                         subscriber.aspirant.alias_name, shortcode)
                sms_menu_log = SMSMenuLog(
                    phone_number=phone_number,
                    date_created=datetime.datetime.now(),
                    menu_type='SURVEY',
                    allowed_options=json.dumps([1]),
                    extra_info=json.dumps({
                        'WAS_QUESTION': 0,
                        'SURVEY_ID': survey_id,
                        'NEXT_QUESTION_NUMBER': 1
                    }))
                sms_menu_log.save()
                sms_util.send_single_sms(phone_number, msg)
                recipient.has_been_notified = True
                recipient.date_notified = datetime.datetime.now()
                recipient.save()
            survey.is_sent = True
            survey.save()
            return_data['STATUS'] = '1'
            return_data['MESSAGE'] = 'Survey has been sent to the set subscribers'
        except Exception, e:
            return_data['STATUS'] = '0'
            return_data['MESSAGE'] = 'Survey failed to be sent. Error {}'.format(str(e))
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def get_survey_analysis(request, survey_id):
    template = 'survey/survey_analysis.html'
    context = {}
    try:
        survey= Survey.objects.get(client=Client.objects.get(user=request.user), id=survey_id)
        questions_list = SurveyQuestion.objects.filter(survey=survey).order_by('id')
        questions_obj = []
        chart_data = []
        for question in questions_list:
            options = SurveyOptions.objects.filter(survey_question=question).order_by('id')
            options_dic = options.values()
            ith_chart_data = []
            for i in range(0, len(options_dic)):
                try:
                    count = SurveyResponse.objects.filter(
                        survey_option=options[i]).count()
                    options_dic[i]['response_count'] = count
                    ith_chart_data.append({
                        'option': options[i].option,
                        'count': count
                    })
                except Exception, e:
                    print(str(e))
                    options_dic[i]['response_count'] = 0
                    pass
            chart_data.append({
                'question_id': question.id,
                'data': ith_chart_data
                })
            questions_obj.append({
                'question': question.question,
                'id': question.id,
                'options': options_dic
            })


        context['survey'] = {
            'survey_title': survey.survey_title,
            'survey_id': survey.id,
            'survey_desc': survey.survey_desc,
            'questions_obj': questions_obj,
            'chart_data': chart_data
        }
    except:
        pass


    return render(request, template, context)








