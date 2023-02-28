from django.urls import path
import accounts.views as AccountsViews
from . import views

urlpatterns = [
   path('',AccountsViews.cust_account,name='customer'),
   path('c_profile/',views.c_profile,name='c_profile'),
   path('my_orders/',views.my_orders,name='my_orders'),
   path('order_details<int:order_number>/',views.order_details,name='order_details'),
]
