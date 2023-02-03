from django import forms
from. models import Category,FoodItem
from accounts.Validator import allow_only_image

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name','description']


class FoodItemForm(forms.ModelForm):
    image = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-50 '}), validators=[allow_only_image])
    image_2 = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-50 '}), validators=[allow_only_image])
    image_3 = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-50 '}), validators=[allow_only_image])
    image_4 = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-50 '}), validators=[allow_only_image])
    image_5 = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-50 '}), validators=[allow_only_image])

    class Meta:
        model = FoodItem
        fields = ['category', 'food_title', 'description', 'price', 'image','image_2','image_3','image_4','image_5',    'is_available']