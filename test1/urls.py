from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from marketplace import views as MarketplaceViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/', include('accounts.urls')),
    #cart
    path('cart/',MarketplaceViews.cart, name='cart'),

    path('marketplace/', include('marketplace.urls')),
    #search path
    path('search/',MarketplaceViews.search,name='search'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

