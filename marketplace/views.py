from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse
from .context_processors import get_cart_amount, get_cart_counter
from marketplace.models import Cart
from vendor.models import Vendor
from menu.models import Category,FoodItem
from django.db.models import Prefetch
from accounts.models import UserProfile
from orders.forms import OrderForm

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count
    }
    return render(request,'marketplace/listing.html',context)

def vendor_detail(request,vendor_slug):
    vendor = get_object_or_404(Vendor,vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset= FoodItem.objects.filter(is_available=True)
        )
    )
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user = request.user)
    else:
        cart_items = None
    context = {
        'vendor':vendor,
        'categories':categories,
        'cart_items':cart_items,
    }

    return render(request,'marketplace/vendor_details.html',context)

def food_details(request,pk=None):
    
    food = FoodItem.objects.get(is_available=True,pk=pk)

    context = {
        
        'food':food,
    }
    return render(request,'marketplace/food_details.html',context)

@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user = request.user).order_by('created_at')
    context = {
        'cart_items':cart_items
    }
    return render(request,'marketplace/cart.html',context)
@login_required(login_url='login')
def add_to_cart(request,food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # check if the food item exist or not
            try:
                fooditem = FoodItem.objects.get(id = food_id)
                # check if the user already added the food or not
                try:
                    chkCart = Cart.objects.get(user = request.user,fooditem = fooditem)
                    # increase the item 
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status':'success','message':'Increased the item ','cart_counter':get_cart_counter(request),'qty':chkCart.quantity,'cart_amount':get_cart_amount(request)})
                except:
                    chkCart = Cart.objects.create(user = request.user,fooditem = fooditem,quantity = 1)
                    return JsonResponse({'status':'success','message':'added the product to the cart','cart_counter':get_cart_counter(request),'qty':chkCart.quantity,'cart_amount':get_cart_amount(request)})
                    
            except:
                return JsonResponse({'status':'failed','message':'food item does not exist'})
        else:
            return JsonResponse({'status': 'success', 'message': 'invalid request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

@login_required(login_url='login')
def decrees_cart(request,food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # check if the food item exist or not
            try:
                fooditem = FoodItem.objects.get(id = food_id)
                # check if the user already added the food or not
                try:
                    chkCart = Cart.objects.get(user = request.user,fooditem = fooditem)
                    if chkCart.quantity > 1:
                        # decrees the item 
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse({'status':'success','cart_counter':get_cart_counter(request),'qty':chkCart.quantity,'cart_amount':get_cart_amount(request)})
                except:
                    return JsonResponse({'status':'success','message':'You dont have item in your cart','qty':chkCart.quantity})
                    
            except:
                return JsonResponse({'status':'failed','message':'food item does not exist'})
        else:
            return JsonResponse({'status': 'success', 'message': 'invalid request'})
       
    else:
        return JsonResponse({'status': 'failed', 'message': 'Please login to continue'})
@login_required(login_url='login')
def delete_cart(request,cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #check if the item is available in the cart
            cart_item = Cart.objects.get(user = request.user,id=cart_id)
            if cart_item:
                cart_item.delete()
                return JsonResponse({'status':'success','message':'item has been deleted','cart_counter':get_cart_counter(request),'cart_amount':get_cart_amount(request)})
        else:
            return JsonResponse({'status':'failed','message':'invalid request'})
    else:
        return JsonResponse({'status':'failed','message':'please login to continue'})

def search(request):
    # address = request.GET['address']
    latitude = request.GET['lat']
    longitude = request.GET['lng']
    radius = request.GET['radius']
    r_name = request.GET['rest_name']

    #get vendor by food item
    get_vendor_by_fooditem = FoodItem.objects.filter(food_title__icontains = r_name,is_available= True).values_list('vendor',flat=True)
    print(get_vendor_by_fooditem)
    vendors = Vendor.objects.filter(vendor_name__icontains = r_name,user__is_active = True,is_approved = True)
    vendor_count = vendors.count()
    context = {
        'vendors':vendors,
        'vendor_count':vendor_count
    }

    print(latitude,longitude,radius,r_name)
    return render(request,'marketplace/listing.html',context)


@login_required(login_url='login')
def checkout(request):
    cart_item = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_item.count()
    if cart_count <= 0:
        return redirect('marketplace')
    user_profile = UserProfile.objects.get(user = request.user)
    default_value = {
        'first_name':request.user.first_name,
        'last_name':request.user.last_name,
        'phone':request.user.phone_number,
        'email':request.user.email,
        'address':user_profile.address,
        'country':user_profile.country,
        'state':user_profile.state,
        'city':user_profile.city,
        'pin_code':user_profile.pin_code

    }
    form = OrderForm(initial=default_value)
    context = {
        'form':form,
        'cart_item':cart_item,
    }
    return render(request,'marketplace/checkout.html',context)