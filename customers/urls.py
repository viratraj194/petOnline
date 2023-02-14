from django.urls import path
import accounts.views as AccountsViews
from . import views

urlpatterns = [
   path('',AccountsViews.cust_account,name='customer'),
   path('c_profile/',views.c_profile,name='c_profile'),
]
