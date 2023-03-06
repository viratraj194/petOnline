from django.shortcuts import render,redirect,HttpResponse
from django.http import HttpResponse, JsonResponse
from marketplace.context_processors import get_cart_amount
from marketplace.models import Cart, Tax
from menu.models import FoodItem
from orders.models import Order, OrderedFood, Payment
from.forms import OrderForm
import simplejson as json
from . utils import generate_order_number
from test1.settings import RZP_KEY_ID,RZP_KEY_SECRET
import razorpay
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required
# Create your views here.

client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))

@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user = request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    vendors_ids = []
    for i in cart_items:
        if i.fooditem.vendor.id  not in vendors_ids:
            vendors_ids.append(i.fooditem.vendor.id)


    get_tax = Tax.objects.filter(is_active = True)
    subtotal = 0
    total_data = {}
    k = {}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk= i.fooditem.id,vendor_id__in=vendors_ids)
        v_id = fooditem.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (fooditem.price * i.quantity)
            k[v_id] = subtotal
        else:
            subtotal = (fooditem.price * i.quantity)
            k[v_id] = subtotal
        #calculate the tax data
        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100,2)
            tax_dict.update({tax_type:{str(tax_percentage):{str(tax_amount)}}})      
            #calculate total data
        total_data.update({fooditem.vendor.id:{str(subtotal):str(tax_dict)}})


    subtotal = get_cart_amount(request)['subtotal']
    total_tax = get_cart_amount(request)['tax']
    grand_total = get_cart_amount(request)['grand_total']
    tax_data = get_cart_amount(request)['tax_dict']
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()
            # Razorpay Payment
            DATA = {
                "amount": float(order.total)*100,
                "currency": "INR",
                "receipt": "receipt # "+order.order_number,
                "notes": {
                    "key1": "value3",
                    "key2": "value2"
                }
            }
            rzp_order = client.order.create(data=DATA)
            rzp_order_id = rzp_order['id'] 
            
            

            context ={
                'order':order,
                'cart_items':cart_items,
                'rzp_order_id':rzp_order_id,
                'RZP_KEY_ID':RZP_KEY_ID,
                'rzp_amount':float(order.total)*100,

            }
            return render(request,'orders/place_order.html',context)
            


        else:
            form.errors()
    return render(request,'orders/place_order.html')

@login_required(login_url='login')
def payments(request):
    #request is ajax or not
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST': 

        #store the payment details in payment models
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        # print(order_number,transaction_id,payment_method,status)
        order = Order.objects.get(user = request.user,order_number=order_number)
        payment = Payment(
            user = request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status
        )
        payment.save()
        #update the order model
        order.payment = payment
        order.is_ordered = True
        order.save()
        # return HttpResponse('save')
        #move the cart items to ordered food
        cart_items = Cart.objects.filter(user = request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity
            ordered_food.save()
        
        #send the order conformation mail to customer
        mail_subjects = 'Thank you for ordering with us'
        mail_template = 'orders/order_conformation_email.html'

        

        context = {
            'user':request.user,
            'order':order,
            'to_email':order.user.email,
            
        }
        send_notification(mail_subjects,mail_template,context)
          
        #order received mail to vendor
        mail_subjects = 'you have received new order.'
        mail_template = 'orders/new_order_received.html'
        to_emails = []
        
        for i in cart_items:
            if i.fooditem.vendor.user.email not in to_emails:
                to_emails.append(i.fooditem.vendor.user.email)
       
                # ordered_food_to_vendor = OrderedFood.objects.filter(order = order,fooditem__vendor = i.fooditem.vendor)
        

        context = {
            'order':order,
            'to_email':to_emails,
            # 'ordered_food_to_vendor':ordered_food_to_vendor,
            # 'vendor_subtotal':order_total_by_vendor(order,i.fooditem.vendor.id)['subtotal'],
            # 'tax_data':order_total_by_vendor(order,i.fooditem.vendor.id)['tax_dict'],
            # 'vendor_grand_total':order_total_by_vendor(order,i.fooditem.vendor.id)['grand_total'],
        }
        send_notification(mail_subjects,mail_template,context)
            
        #clear the cart if the payment is success
        # cart_items.delete()
        #return back to ajax with status success or failure
        response = {
            'order_number':order_number,
            'transaction_id':transaction_id
        }
        return JsonResponse(response)
    return HttpResponse('payments view')




def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')
    try:
        order = Order.objects.get(order_number=order_number,payment__transaction_id = transaction_id,is_ordered = True)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        for item in ordered_food:
            subtotal = (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)
        context = {
            'order':order,
            'ordered_food':ordered_food,
            'subtotal':subtotal,
            'tax_data':tax_data,
        }
        return render(request,'orders/order_complete.html',context)
    except:
        return redirect('home')

