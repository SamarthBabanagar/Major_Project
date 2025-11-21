from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class AadhaarRequestOTPForm(forms.Form):
    aadhaar_number = forms.CharField(label="Aadhaar Number", max_length=12)

class AadhaarVerifyOTPForm(forms.Form):
    aadhaar_number = forms.CharField(widget=forms.HiddenInput())
    txnId = forms.CharField(widget=forms.HiddenInput())
    otp = forms.CharField(label="Enter OTP", max_length=10)

# class AuthenticationForm(forms.Form):
#     username = forms.CharField()
#     password = forms.CharField(widget=forms.PasswordInput)
