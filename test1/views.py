from django.shortcuts import render
from menu.models import Category, FoodItem
from vendor.models import Vendor

def home(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    print(vendors)
    context = {
        'vendors':vendors
    }
    return render(request, 'accounts/home.html',context)


def adoption(request):
    fooditems  = FoodItem.objects.filter(price = 0) 
    fooditems_count = fooditems.count()
    print(fooditems)

    # vendors_ids = []
    # for i in fooditems:
    #     if i.vendor.id not in vendors_ids:
    #         vendors_ids.append(i.vendor.id)

    # print(vendors_ids)
    # for i in vendors_ids:

    #     vendors = Vendor.objects.filter(pk=i)
    #     print(vendors)


    context = {
        'fooditems':fooditems,
        'fooditems_count':fooditems_count
        
    }
    return render(request,'accounts/adoption.html',context)