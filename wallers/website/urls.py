from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.home, name='home',),
    path('cart/', views.cart, name='cart',),
    path('checkout/', views.checkout, name='checkout',),
    path('update_item/', views.updateItem, name='update_item',),
    path('cart/update_item/', views.updateItem, name='update_item',),
    path('contact/', views.contact, name='contact',),
    path('process_order/', views.processOrder, name='process_order',),
    path('checkout/process_order/', views.processOrder, name='process_order',),
    path('orders/', views.orders, name='orders',),
    path('order/<str:transaction_id>', views.order, name='order',),
    path('orders/change_status/', views.change_status, name='change_status',),
]