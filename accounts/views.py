from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from orders.models import Order

from vendor.models import Vendor
from .forms import UserForm
from vendor.forms import VendorForm
from .models import User, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from .utils import detectUser, send_verification_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator





def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in')
        return redirect('account')
    elif request.method == 'POST':
        # print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, 'your registration is successfully! please wait for approval.'.title())
            return redirect('home')
        else:
            # messages.error(request, 'there is some error in registration'.title())
            print('invalid form')
            print(form.errors)
    else:

        form = UserForm
    context = {
        'form': form
    }

    return render(request, 'accounts/registerUser.html', context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in')
        return redirect('account')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['last_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email,
                                            password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            # send email verification
            mail_subject = 'please activate your account'.title()
            mail_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, mail_template)
            # send_verification_email(request, user)
            messages.success(request, 'your account has been registered successfully! please wait for approval')
            return redirect('registerVendor')
        else:
            print('invalid form')
            print(form.errors)

    else:
        form = UserForm()
        v_form = VendorForm
    context = {
        'form': form,
        'v_form': v_form
    }

    return render(request, 'accounts/registerVendor.html', context)


# activate user by setting the activation status true

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'your account is activated'.title())

        return redirect('account')
    else:
        messages.error(request, 'invalid activation link'.title())
        return redirect('account')


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in')
        return redirect('account')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            print('success')
            messages.success(request, 'you have logged in successfully!'.title())
            return redirect('account')
        else:
            messages.success(request, 'something went wrong!'.title())
            return redirect('login')

    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.success(request, 'you have logged out successfully'.title())
    return redirect('login')


@login_required(login_url='login')
def account(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)


# restrict user from going in to the costumer dashboard
def check_user_role_for_cost(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def check_user_role_for_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# dashboard
@login_required(login_url='login')
@user_passes_test(check_user_role_for_vendor)
def vendor_account(request):

    return render(request, 'accounts/vendor_account.html', )


@login_required(login_url='login')
@user_passes_test(check_user_role_for_cost)
def cust_account(request):
    orders = Order.objects.filter(user = request.user,is_ordered = True)
    recent_orders = orders[:5]

    context = {
        'orders':orders,
        'orders_count':orders.count(),
        'recent_orders':recent_orders,
    }
    return render(request, 'accounts/cust_account.html',context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact = email)
            mail_subject = 'please click below link to reset password'.title()
            mail_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, mail_template)
            messages.info(request, 'reset password link is sent your email'.title())
            return redirect('login')
        else:
            messages.error(request, "email didn't match".title())
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError,User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'please reset your password'.title())
        return redirect('reset_password')
    else:
        messages.error(request, " 'email didn't exist".title())
        return redirect('account')




def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        conform_password = request.POST['conform_password']
        if password == conform_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request,'password reset is successful'.title())
            return redirect('login')
        else:
            messages.error(request, 'password did not match'.title())
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')
