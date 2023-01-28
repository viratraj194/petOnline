from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse
from .context_processors import get_cart_counter
from marketplace.models import Cart
from vendor.models import Vendor
from menu.models import Category,FoodItem
from django.db.models import Prefetch

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
                    return JsonResponse({'status':'success','message':'Increased the item ','cart_counter':get_cart_counter(request),'qty':chkCart.quantity})
                except:
                    chkCart = Cart.objects.create(user = request.user,fooditem = fooditem,quantity = 1)
                    return JsonResponse({'status':'success','message':'added the product to the cart','cart_counter':get_cart_counter(request),'qty':chkCart.quantity})
                    
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
                    return JsonResponse({'status':'success','cart_counter':get_cart_counter(request),'qty':chkCart.quantity})
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
                return JsonResponse({'status':'success','message':'item has been deleted','cart_counter':get_cart_counter(request)})
        else:
            return JsonResponse({'status':'failed','message':'invalid request'})
    else:
        return JsonResponse({'status':'failed','message':'please login to continue'})