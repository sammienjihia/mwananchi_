from django import forms
from models import Subscriber
from region.models import Country,County,Constituency,Ward
from django.contrib.auth.models import User

from language.models import Language

class SubscriberForm(forms.ModelForm):
    first_name = forms.CharField(max_length=15,label='First Name',widget=forms.TextInput(attrs={'placeholder':'First Name','class' : 'w3-input w3-text-blue text-capitalize','autofocus':'autofocus'}))
    last_name = forms.CharField(max_length=15,label='Last Name',widget=forms.TextInput(attrs={'placeholder':'Last Name','class' : 'w3-input w3-text-blue text-capitalize','autofocus':'autofocus'}))
    gender = forms.ChoiceField(widget = forms.Select(),choices=([('Male','Male'),('Female','Female')]),required=True)
    date_of_birth = forms.DateField(label='Date of Birth',widget=forms.DateInput(attrs={'class': 'w3-input w3-text-blue datepicker-required','autofocus':'autofocus'}))
    phone_number = forms.CharField(max_length=255, label='Phone Number',widget=forms.TextInput(attrs={'placeholder':'Phone number','class' : 'w3-input w3-text-blue text-capitalize','autofocus':'autofocus'}))
    email_address = forms.CharField(max_length=255, label='Email',widget=forms.TextInput(attrs={'placeholder':'Email address','class' : 'w3-input w3-text-blue text-capitalize','autofocus':'autofocus'}),required=False)

    language = forms.ModelChoiceField(queryset=Language.objects.all(),label='Language')

    county = forms.ModelChoiceField(queryset=County.objects.all(), widget=forms.Select(), label='County')

    constituency = forms.ModelChoiceField(queryset=Constituency.objects.all(), widget=forms.Select(), label='Constituency',required=False)
    ward = forms.ModelChoiceField(queryset=Ward.objects.all(), widget=forms.Select(), label='Ward',required=False)

    class Meta:
        model = Subscriber
        fields = [
            'first_name',
            'last_name',
            'gender',
            'date_of_birth',
            'phone_number',
            'email_address',
            'language',
            'county',
            'constituency',
            'ward',
        ]

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if Subscriber.objects.filter(phone_number=self.cleaned_data.get('phone_number')):
            raise forms.ValidationError("This mobile number is already subscribed")
        return phone_number
