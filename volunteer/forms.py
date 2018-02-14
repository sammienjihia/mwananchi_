from django import forms
from models import Volunteer
from region.models import Country,County,Constituency,Ward
from django.contrib.auth.models import User

class VolunteerForm(forms.Form):
    first_name = forms.CharField(max_length=15,label='First Name',widget=forms.TextInput(attrs={'placeholder':'First Name','class' : 'w3-input w3-text-blue text-capitalize','autofocus':'autofocus'}))
    last_name = forms.CharField(max_length=15,label='Last Name',widget=forms.TextInput(attrs={'placeholder':'Last Name','class' : 'w3-input w3-text-blue text-capitalize',}))
    email= forms.CharField(label='Email',widget=forms.TextInput(attrs={'placeholder':'name@example.com','class' : 'w3-input w3-text-blue','autofocus':'autofocus'}),required=True)
    phone_number = forms.CharField(max_length=13,label='Phone Number',widget=forms.TextInput(attrs={'placeholder':'0700xxxxxx','class' : 'w3-input w3-text-blue phone-formatted'}))
    password = forms.CharField(label= 'Password',widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class' : 'w3-input w3-text-blue'}))
    confirm_password = forms.CharField(label='Confirm password',
                               widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'class': 'w3-input w3-text-blue'}))

    county = forms.ModelChoiceField(queryset=County.objects.all(), widget=forms.Select(), label='County')
    constituency = forms.ModelChoiceField(queryset=Constituency.objects.all(), widget=forms.Select(), label='Constituency',required=False)
    ward = forms.ModelChoiceField(queryset=Ward.objects.all(), widget=forms.Select(), label='Ward',required=False)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if Volunteer.objects.filter(phone_number=self.cleaned_data.get('phone_number')):
            raise forms.ValidationError("This mobile number is already subscribed")
        return phone_number

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('confirm_password')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        if len(password2) < 8:
            raise forms.ValidationError(
                self.error_messages['password_too_short'],
                code='password_too_short',
            )

        return password2

