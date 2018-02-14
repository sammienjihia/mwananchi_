import datetime
import json

from django.core import serializers
from django.db.models import Q
from django.utils.timezone import now
from django.contrib.auth.models import User

from sms.models import  Outbox
from subscribers.models import Subscriber

from client.models import Client
from campaign.models import Campaign, CampaignItems
from sms.models import SMSMenuLog



from app_utility.excel_utils import ExcelFile


from Mwananchi.AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException


class SMS:
    def __init__(self):
        self.__username = "SAMMIENJIHIA"
        self.__api_key = "9898e481449e39a6051b3d87e07f4de171bedc93a046dd166c0dad2d0d9b6bdc"

    def send_batch_sms_from_excel_upload(self, file_name, message_template, user):
        excel_file = ExcelFile(file_name)
        file_headers = excel_file.get_header()
        records = excel_file.get_records(True)
        try:
            user = serializers.deserialize("json", user).next().object
        except:
            user = User.objects.get(id=user)

        for record in records:
            template_vals = {
                file_headers[i]: str(record[i]).strip() for i in range(0, len(file_headers))
                }

            message = self.create_message_from_template(message_template, template_vals)
            phone_number = record[0]
            phone_number = str(phone_number)
            phone_number = phone_number.replace(' ', '')
            to = self.format_phone_number(phone_number)
            date_sent = datetime.datetime.now()

            send_sms = self.__send_sms(to, message)

            if send_sms is True:
                outbox = Outbox(phone_number=to,
                                message=message,
                                is_sent=True,
                                date_sent=date_sent,
                                user=user
                                )
                try:
                    outbox.subscriber = Subscriber.objects.get(client=Client.objects.get(user=user),
                                                               phone_number=to)

                except:
                    pass

                outbox.save()

            else:
                outbox = Outbox(phone_number=to,
                                message=message,
                                is_sent=False,
                                date_sent=date_sent,
                                user=user
                                )
                try:
                    print (phone_number)
                    print (to)
                    outbox.subscriber = Subscriber.objects.get(client=Client.objects.get(user=user),
                                                               phone_number=to)

                except:
                    pass

                outbox.save()

    def send_batch_sms_from_recipient_list(self, recipient_list, message, user):
        try:
            user = serializers.deserialize("json", user).next().object
        except:
            user = User.objects.get(id=user)

        for phone_number in recipient_list:
            phone_number = str(phone_number)
            phone_number = phone_number.replace(' ', '')
            to = self.format_phone_number(phone_number)
            date_sent = datetime.datetime.now()
            send_sms = self.__send_sms(to, message)

            if send_sms is True:
                outbox = Outbox(phone_number=to,
                                message=message,
                                is_sent=True,
                                date_sent=date_sent,
                                user=user,
                                message_type='CHAT'
                                )
                try:
                    outbox.subscriber = Subscriber.objects.get(client=Client.objects.get(user=user),
                                                               phone_number=to)

                except:
                    pass

                outbox.save()
            else:
                print (phone_number)
                print (to)
                outbox = Outbox(phone_number=to,
                                message=message,
                                is_sent=False,
                                date_sent=date_sent,
                                user=user,
                                message_type = 'CHAT'
                                )
                try:
                    outbox.subscriber = Subscriber.objects.get(client=Client.objects.get(user=user),
                                                               phone_number=to)

                except:
                    pass

                outbox.save()

    def send_batch_sms_to_all_subscribers(self, user_id, phone_numbers, message):
        user = User.objects.get(id=user_id)
        print(phone_numbers)
        recipients = json.loads(phone_numbers)
        for phone_number in recipients:
            to = self.format_phone_number(phone_number)
            subscriber = Subscriber.objects.get(phone_number=phone_number, client=Client.objects.get(user=user))
            date_sent = datetime.datetime.now()
            send_sms = self.__send_sms(to, message)

            if send_sms is True:
                outbox = Outbox(phone_number=to,
                                message=message,
                                is_sent=True,
                                date_sent=date_sent,
                                user=user,
                                message_type='CHAT',
                                subscriber=subscriber)
                outbox.save()
            else:
                outbox = Outbox(phone_number=to,
                                message=message,
                                is_sent=False,
                                date_sent=date_sent,
                                user=user,
                                message_type='CHAT',
                                subscriber=subscriber)

                outbox.save()

    def filter_sms_recipients(self, subscriber_filters):
        def date_range(min_age, max_age):
            min_age = int(min_age)
            max_age = int(max_age)
            current = now().date()
            min_date = datetime.date(current.year - min_age, current.month, current.day)
            max_date = datetime.date(current.year - max_age, current.month, current.day)
            return min_date, max_date

        min_age = str(subscriber_filters['min_age'])
        max_age = str(subscriber_filters['max_age'])

        gender = subscriber_filters['gender']

        if len(subscriber_filters['county_id']) > 0 and subscriber_filters['county_id'] != 'NULL':
            county_id = int(subscriber_filters['county_id'])
        else:
            county_id = None

        if len(subscriber_filters['constituency_id']) > 0 and subscriber_filters['constituency_id'] != 'NULL':
            constituency_id = int(subscriber_filters['constituency_id'])
        else:
            constituency_id = None

        if len(subscriber_filters['ward_id']) > 0 and subscriber_filters['ward_id'] != 'NULL':
            ward_id = int(subscriber_filters['ward_id'])
        else:
            ward_id = None

        if gender == 'NULL' or len(gender) == 0:
            gender = None

        new_filters = {
            'gender': gender,
            'county_id': county_id,
            'constituency_id': constituency_id,
            'ward_id': ward_id
        }

        subscribers = Subscriber.objects.filter(client=Client.objects.get(user=subscriber_filters['user']))
        if len(min_age) > 0 and len(max_age) > 0:
            date_range = date_range(min_age, max_age)
            subscribers.filter(Q(Q(date_of_birth__gte=date_range[1]) & Q(date_of_birth__lte=date_range[0])))

        for key, value in new_filters.items():
            if value is not None:
                subscribers = subscribers.filter(**{key: value})
        return subscribers

    def format_phone_number(self, phone_number):
        to = ''
        phone_number = str(phone_number)
        if phone_number[0: 4] == '+254':
            to = phone_number
        elif phone_number[0: 4] == '2547':
            to = '+' + str(phone_number)
        elif phone_number[0: 2] == '07':
            to = '+254' + phone_number[1: ]
        elif phone_number[0: 1] == '7':
            to = '+254' + phone_number
        return to

    def create_message_from_template(self, message_template, template_vals):
        start_index = 0
        i = 0

        while i < len(message_template):
            left_index = message_template.find('[', start_index)
            right_index = message_template.find(']', start_index)
            start_index = right_index
            if left_index is -1 or right_index is -1:
                break
            template_val_name = message_template[left_index+1: right_index]
            start_index += (len(template_vals[template_val_name]) - len('['+template_val_name+']'))
            message_template = message_template.replace('['+template_val_name+']', template_vals[template_val_name])
            i += start_index
        return message_template

    def __send_sms(self, to, message):
        try:
            sms_gateway = AfricasTalkingGateway(self.__username, self.__api_key)
            response = sms_gateway.sendMessage(to, message)
            if response[0]['STATUS'] == 'Success':
                return True
            else:
                return False
        except AfricasTalkingGatewayException:
            return False
        except Exception, e:
            return False

    def send_single_sms(self, to, message):
        try:
            sms_gateway = AfricasTalkingGateway(self.__username, self.__api_key)
            response = sms_gateway.sendMessage(to, message)
            print(response)
            if response[0]['status'] == 'Success':
                return True
            else:
                return False

        except AfricasTalkingGatewayException:
            return False
        except Exception, e:
            return False


    def send_manifesto_to_subscribers(self, manifesto, aspirant):
        manifesto = serializers.deserialize("json", manifesto).next().object
        aspirant = serializers.deserialize("json", aspirant).next().object

        manifesto_language = manifesto.language
        manifesto_items = CampaignItems.objects.filter(campaign=manifesto)
        subscribers = Subscriber.objects.filter(Q(client=aspirant)
                                                & Q(Q(language=manifesto_language) | Q(language=None)))
        manifesto_headings = [item.title for item in manifesto_items]
        manifesto_ids = [item.id for item in manifesto_items]
        sms_util = SMS()
        short_code = '12345'

        for subscriber in subscribers:
            message = ""
            try:
                if len(subscriber.first_name) > 0:
                    message = """Dear {}, send an sms to {} with any of the options below to view Nairobi's budget campaign\n""".format(
                        subscriber.first_name, short_code)
            except:
                message = """Dear subscriber, send an sms to {} with any of the options below to view Nairobi's budget campaign\n""".format(
                     short_code)
            fall_back_sms = """Invalid option. Send an sms to {} with any of the options below to view Nairobi's budget campaign\n""".format(short_code)

            allowed_options = []
            options_mapping = {}
            for i in range(0, len(manifesto_headings)):
                message += "{} . {}\n".format(i + 1, manifesto_headings[i])
                fall_back_sms += "{} . {}\n".format(i + 1, manifesto_headings[i])
                allowed_options.append(i + 1)
                options_mapping[i + 1] = manifesto_ids[i]
            phone_number = sms_util.format_phone_number(subscriber.phone_number)

            sms_menu_log = SMSMenuLog(
                date_created=datetime.datetime.now(),
                phone_number=phone_number,
                menu_type='MANIFESTO',
                allowed_options=json.dumps(allowed_options),
                extra_info=json.dumps({
                    'MANIFESTO_ID': manifesto.id,
                    'FALL_BACK_SMS':fall_back_sms,
                    'OPTIONS_MAPPING': options_mapping
                }))

            try:
                sms_menu_log.save()
                self.__send_sms(phone_number, message)
                #Log campaign recipient
            except:
                #Log error on sending campaign
                pass



