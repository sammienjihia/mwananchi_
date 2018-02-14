from django import forms


class Twitter_SearchForm(forms.Form):
    searchword = forms.CharField(max_length=255, label='', widget=forms.TextInput(attrs={
        'class':'w3-input w3-col l4 m4 s4',
        'placeholder': 'Search twitter',
        'autofocus': 'autofocus'
    }))
