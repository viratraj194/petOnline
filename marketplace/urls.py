from django.urls import path
from . import views


urlpatterns = [
    path('',views.marketplace,name='marketplace'),
    path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),
    path('food_details/<int:pk>/',views.food_details, name='food_details'),
    # add to cart
    path('add_to_cart/<int:food_id>',views.add_to_cart,name='add_to_cart'),
    # DECREES cart
    path('decrees_cart/<int:food_id>',views.decrees_cart,name='decrees_cart'),
    #Delete the cart
    path('delete_cart/<int:cart_id>',views.delete_cart,name='delete_cart'),
]
