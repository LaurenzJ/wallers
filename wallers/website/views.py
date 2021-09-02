from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse
from django.template.loader import get_template

import json
import datetime
from xhtml2pdf import pisa

from store.models import *
from store.utils import cookieCart, cartData, guestOrder
from django.urls import reverse


def home(request):
    items = Item.objects.all().order_by('uploaded_on')
    selected = ""

    if 'search' in request.GET:
        keywords = request.GET['search']
        if keywords:
            items = items.filter(name__icontains=keywords)    
    
    if 'category' in request.GET:
        selected = request.GET['category']
        keywords = request.GET['category']
        if keywords:
            items = items.filter(category__icontains=keywords)    

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        
    context = {
        "items": items,
        "order": order,
        "selected": selected,
    }

    if request.user.is_superuser:
        orders = Order.objects.filter(complete=True).order_by('delivery_date')
        context['orders'] = orders
    
    return render(request, 'website/index.html', context)


def cart(request):
    orders = Order.objects.filter(complete=True).order_by('delivery_date')
    data = cartData(request)
    
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
        
    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'orders': orders,
    }
    
    return render(request, 'website/cart.html', context)

@ensure_csrf_cookie
def checkout(request):
    orders = Order.objects.filter(complete=True).order_by('delivery_date') # get all the completed orders
    data = cartData(request) # get cart data from user or cookies
    
    # split cart data into objects
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {
        'order': order,
        'orders': orders, 
    }

    return render(request, 'website/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body) # get the data from request.body
    productId = data['productId'] # get product id from data
    action = data['action'] # get action from data
    amount = data['amount'] # get amount from data  

    customer = request.user.customer
    product = Item.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    elif action == 'delete':
        orderItem.quantity = 0
    elif action == 'add_mulitple':
        orderItem.quantity = (orderItem.quantity + amount)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)

@ensure_csrf_cookie
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'].replace(',', '.')) # replace -> so no error in conversion occurs
    order.transaction_id = transaction_id
    order.delivery_date = data['shipping']['delivery_date']
    order.comment = data['shipping']['comment']

    if total == float(order.get_cart_total):
        order.complete = True
    order.save() 

    ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        zipcode=data['shipping']['zipcode'],
    )

    return JsonResponse('Buy Order complete!', safe=False)

@staff_member_required
def orders(request):
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    if request.user.is_superuser:
        orders = Order.objects.filter(complete=True).order_by('delivery_date')

        selected = ""
        is_finished = "off"

        if 'order_by' in request.GET:
            selected = request.GET['order_by']
            if selected == 'delivery_date-asc':
                orders = orders.order_by('delivery_date') 
            elif selected == 'delivery_date-desc':
                orders = orders.order_by('-delivery_date')
        
        if 'is_finished' in request.GET:
            is_finished = request.GET['is_finished']
            if is_finished == 'on':
                orders = orders.exclude(finished=True)
            else:
                orders = orders.exclude(finished=False)

        if 'search' in request.GET:
            keywords = request.GET['search']
            if keywords:
                orders = orders.filter(transaction_id__icontains=keywords)  


        context = {
            'orders': orders,
            'order': order,
            'selected': selected,
            'is_finished': is_finished,
        } 
    else:
        context = {}

    return render(request, 'website/orders.html', context)


def order(request, transaction_id):
    order = Order.objects.get(transaction_id=transaction_id)

    template_path = 'website/order_pdf.html'
    context = {'order': order}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response

@staff_member_required
def add_product(request):
    orders = Order.objects.filter(complete=True).order_by('delivery_date')
    order = Order.objects.get(customer=request.user.customer, complete=False)

    context = {
        'orders': orders,
        'order': order,
    }

    return render(request, 'website/add_product.html', context=context)


@staff_member_required()
def change_status(request):
    transaction_id = request.GET['transaction_id']
    order = Order.objects.get(transaction_id=transaction_id)
    order.finished = not order.finished
    order.save()

    status = '(Abgeschlossen)' if order.finished else '(Offen)'
    

    return HttpResponse(status)

def contact(request):
    print(request.body)
    # data = json.loads(request)
    # if request.user.is_authenticated:
    #     customer = request.user.customer
    #     order, created = Order.objects.get_or_create(customer=customer, complete=False)
    # else:
    #     customer, order = guestOrder(request, data)

    # context = {
    #     'order': order,
    # }

    context = {}

    return render(request, 'website/contact.html', context=context)
    