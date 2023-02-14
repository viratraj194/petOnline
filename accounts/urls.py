from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.account),

    path('registerUser', views.registerUser, name='registerUser'),
    path('registerVendor', views.registerVendor, name='registerVendor'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name ='logout'),
    path('account/', views.account, name='account'),
    path('vendor_account/', views.vendor_account, name='vendor_account'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('cust_account/', views.cust_account, name='cust_account'),


    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>/', views.reset_password_validate, name='reset_password_validate'),
    path('reset_password/', views.reset_password, name='reset_password'),

    path('vendor/', include('vendor.urls')),
    path('customers/',include('customers.urls')),




]
