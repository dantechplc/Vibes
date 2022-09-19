from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth import get_user_model
from django import forms
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(
        label='Enter Username', min_length=4, max_length=50, )
    email = forms.EmailField(max_length=100, error_messages={
        'required': 'Sorry, you will need an email'})
    country = CountryField().formfield(required=True)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_password2(self):
        cd = self.cleaned_data  # cd means cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('Passwords do not match.')
        return cd['password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Please use another Email, that is already taken')
        return email

    def clean_country(self):
        country = self.cleaned_data['country']
        return country

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form__input mb-3', 'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update(
            {'class': 'form__input mb-3', 'placeholder': 'E-mail', 'name': 'email', 'id': 'id_email'})
        self.fields['password1'].widget.attrs.update(
            {'class': 'form__input', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form__input', 'placeholder': 'Repeat Password'})
        self.fields['country'].widget.attrs.update(
            {'class': 'form-control', })


class LoginForm(forms.Form):
    email = forms.EmailField(label=_('Email'), error_messages={'required': _('Please enter an email address')})
    password = forms.CharField(label=_('Password'),
                               widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email']
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        return password

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'id': 'email','placeholder': 'Enter Email Address'})
        self.fields['password'].widget.attrs.update({'type': 'password','id':'pass','placeholder': 'Enter Password'})
