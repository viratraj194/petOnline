from django import forms
from .models import User, UserProfile
from accounts.Validator import allow_only_image


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'password'}),
                               min_length=8)
    conform_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'conform password'}), min_length=8)

    class Meta:
        model = User

        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        conform_password = cleaned_data.get('conform_password')
        if password != conform_password:
            raise forms.ValidationError("password didn't match. ")


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_image])
    cover_photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}),validators=[allow_only_image])
    # latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    # longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_photo', 'address','country', 'state', 'city',
                  'pin_code']

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','phone_number']