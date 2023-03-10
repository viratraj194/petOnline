from vendor.models import Vendor
from test1 import settings

def get_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except:
        vendor =None
    return dict(vendor=vendor)


def get_google_api(request):

    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}


def get_paypal_clint_id(request):
    return{'PAYPAL_CLINT_ID':settings.PAYPAL_CLINT_ID}