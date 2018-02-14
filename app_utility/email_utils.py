from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from accounts.tokens import password_reset_token
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings


class SendEmail:
    def __init__(self):
        pass

    def send_email(self,recipients,request, txt_template, html_template):
        return_arr = []
        for recipient in recipients:
            data = {
                'email':recipient.email,
                'domain': request.META['HTTP_HOST'],
                'site-name':'Brandsense',
                'uid':urlsafe_base64_encode(force_bytes(recipient.pk)),
                'user':recipient,
                'token':password_reset_token.make_token(User.objects.get(id=recipient.pk)),
                'protocol':'http',
            }
            sender = settings.EMAIL_HOST_USER
            plaintext = get_template(txt_template)
            htmly = get_template(html_template)
            subject, from_email, to = 'Brandsense Account', sender, recipient.email
            text_content = plaintext.render(data)
            html_content = htmly.render(data)
            try:
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                return_arr.append({
                    'EMAIL': recipient,
                    'STATUS': '1'
                })
            except Exception, exp:
                print('{}'. format(str(exp)))
                return_arr.append({
                    'EMAIL': recipient,
                    'STATUS': '0'
                })
        return return_arr

    def tuma_mail(self, recipients, txt_template, html_template):

        for recipient in recipients:
            data = {
                'user':recipient
            }
            sender = settings.EMAIL_HOST_USER
            plaintext = get_template(txt_template)
            htmly     = get_template(html_template)
            subject, from_email, to = 'Brandsense Account', sender, recipient.email
            text_content = plaintext.render(data)
            html_content = htmly.render(data)
            try:
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except:
                return False
        return True


