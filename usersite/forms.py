from django import forms
from adminsite.models import CustomUser, Address
from django.contrib.auth.forms import PasswordChangeForm


class UsersideEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "username", "email", "phone_number","image")
        widgets = {
            'first_name':forms.TextInput(attrs={'class':'form-control'}),
            'last_name':forms.TextInput(attrs={'class':'form-control'}),
            'username':forms.TextInput(attrs={'class':'form-control'}),
            'email':forms.TextInput(attrs={'class':'form-control'}),
            'phone_number':forms.NumberInput(attrs={'class':'form-control'}),
        }


class PasswordChageFormCustom(PasswordChangeForm):
    class Meta:
        fields = '__all__'
        widgets = {
            
        }