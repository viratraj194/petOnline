from django.shortcuts import  get_object_or_404,redirect,render

from orders.models import Order, OrderedFood
from .forms import VendorForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from .models import Vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from menu.forms import CategoryForm,FoodItemForm
from django.template.defaultfilters import slugify
from menu.models import Category,FoodItem





def check_role_for_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied
        



#ristrict user from going in to the costumer dashboard
def check_role_for_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied

def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

@login_required(login_url='login')
@user_passes_test(check_role_for_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user = request.user)
    vendor = get_object_or_404(Vendor, user = request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance= profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'profile saved'.title())
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    profile_form = UserProfileForm(instance=profile)
    vendor_form = VendorForm(instance=vendor)
    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }
    return render(request, 'accounts/vendor/vprofile.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_for_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    
    context = {
        'categories':categories
    }

    return render(request, 'accounts/vendor/menu_builder.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_for_vendor)
def fooditems_by_category(request,pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category,pk=pk)
    fooditems = FoodItem.objects.filter(vendor = vendor,category= category)
    context = {
        'fooditems':fooditems,
        'category':category
    }
    return render(request,'accounts/vendor/fooditems_by_category.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_for_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)

            category.save()  # here the category id will be generated
            category.slug = slugify(category_name) + '-' + str(category.id)  # chicken-15
            category.save()
            messages.success(request, 'Category Added successfully'.title())
            return redirect('menu_builder')
        else:
            # messages.error(request,form.errors)
            print(form.errors)
    else:
        form = CategoryForm()

    context = {
        'form': form,
    }
    return render(request,'accounts/vendor/add_category.html',context)


@login_required(login_url='login')
@user_passes_test(check_role_for_vendor)
def edit_category(request,pk=None):
    category = get_object_or_404(Category,pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST,instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)

            category.save()  # here the category id will be generated
            category.slug = slugify(category_name) + '-' + str(category.id)  # chicken-15
            category.save()
            messages.success(request, 'Category updated successfully'.title())
            return redirect('menu_builder')
        else:
            # messages.error(request,form.errors)
            print(form.errors)
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category':category,
    }
    return render(request,'accounts/vendor/edit_category.html',context)


@login_required(login_url='login')
@user_passes_test(check_role_for_vendor)
def delete_category(request,pk=None):
    category = get_object_or_404(Category,pk=pk)
    category.delete()
    messages.success(request,'Category deleted successfully'.title())
    return redirect('menu_builder')

@login_required(login_url='login')
@user_passes_test(check_role_for_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST,request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_title) + '-' + str(food.id)
            form.save()
            messages.success(request, 'food Added successfully'.title())
            return redirect('fooditems_by_category', food.category.id)
        else:
            # messages.error(request,form.errors)
            print(form.errors)

    else:
        form = FoodItemForm()
        # modify this form
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
    }
    
    return render(request,'accounts/vendor/add_food.html',context)
@login_required(login_url='login')
@user_passes_test(check_role_for_vendor)
def edit_food(request,pk=None):
    food = get_object_or_404(FoodItem,pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST,request.FILES, instance= food)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            form.save()
            messages.success(request, 'food item  updated successfully'.title())
            return redirect('fooditems_by_category', food.category.id)
        else:
            # messages.error(request,form.errors)
            print(form.errors)

    else:
        form = FoodItemForm(instance=food)
        # modify this form
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
        'food':food,
    }
    
    return render(request,'accounts/vendor/edit_food.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_for_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, 'food item has Deleted successfully'.title())
    return redirect('fooditems_by_category', food.category.id)


def vendor_order_detail(request,order_number):
    try:
        order = Order.objects.get(order_number = order_number,is_ordered = True)
        ordered_food = OrderedFood.objects.filter(order = order,fooditem__vendor=get_vendor(request))
        
        context = {
            'order':order,
            'ordered_food':ordered_food,
            'subtotal':order.get_total_by_vendor()['subtotal'],
            'tax_dict':order.get_total_by_vendor()['tax_dict'],
            'grand_total':order.get_total_by_vendor()['grand_total']
        }
    except:
        return redirect('vendor')
    return render(request,'accounts/vendor/vendor_order_detail.html',context)

def vendor_my_orders(request):
    vendor = Vendor.objects.get(user = request.user)
    orders = Order.objects.filter(vendors__in = [vendor.id],is_ordered = True).order_by('-created_at')
    context = {
        'orders':orders,
    }
    return render(request,'accounts/vendor/vendor_my_orders.html',context)