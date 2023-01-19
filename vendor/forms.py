from django import forms
from .models import Vendor
from accounts.Validator import allow_only_image

class VendorForm(forms.ModelForm):
    vendor_licence = forms.ImageField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_image])

    class Meta:

        model = Vendor
        fields = ['vendor_name', 'vendor_licence']