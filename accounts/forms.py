from django import forms

class SetPasswordForm(forms.Form):
    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
        'password_too_short': 'Password too short. Minimum length is 8 characters.'
       }
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'New Password','class' : 'w3-input w3-text-blue','autofocus':'autofocus'}),label='')
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirm New Password','class' : 'w3-input w3-text-blue','autofocus':'autofocus'}),label='')

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
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


class PasswordResetRequestForm(forms.Form):
    email_or_username = forms.CharField(label="",max_length=254,
                                        widget=forms.TextInput(attrs={'placeholder':'Email or Username',
                                                                      'class' : 'w3-input',
                                                                      'autofocus':'autofocus'}))
