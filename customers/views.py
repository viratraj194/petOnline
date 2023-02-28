from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from accounts.forms import UserInfoForm, UserProfileForm
from django.contrib import messages
from accounts.models import UserProfile
from orders.models import Order, OrderedFood
import simplejson as json


@login_required(login_url='login')
def c_profile(request):
    profile = get_object_or_404(UserProfile,user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES,instance=profile)
        user_form = UserInfoForm(request.POST,instance=request.user)
        if profile_form and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request,'profile has been updated'.title())
            return redirect('c_profile')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)

    context = {
        'profile_form':profile_form,
        'user_form':user_form,
        'profile':profile
    }

    return render(request,'customer/c_profile.html',context)


def my_orders(request):
    orders = Order.objects.filter(user = request.user,is_ordered = True).order_by('-created_at')
    context = {
        'orders':orders,
    }
    return render(request,'customer/my_orders.html',context)


def order_details(request,order_number):
    try:
        order = Order.objects.get(order_number=order_number,is_ordered = True)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)
        context = {
            'order':order,
            'ordered_food':ordered_food,
            'tax_data':tax_data,
            'subtotal':subtotal,
        }
    except:
        return redirect('customer')

    return render(request,'customer/order_details.html',context)
    