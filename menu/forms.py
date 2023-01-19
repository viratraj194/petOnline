from django import forms
from. models import Category,FoodItem
from accounts.Validator import allow_only_image

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name','description']


class FoodItemForm(forms.ModelForm):
    image = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-50 '}), validators=[allow_only_image])

    class Meta:
        model = FoodItem
        fields = ['category', 'food_title', 'description', 'price', 'image', 'is_available']