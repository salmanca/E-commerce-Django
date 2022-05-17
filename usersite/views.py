from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from adminsite.models import *
import random
import os
from twilio.rest import Client
from adminsite.models import CustomUser
import json
from adminsite.forms import AddressForm, CouponUserForm
from usersite.forms import UsersideEditForm
import razorpay
from datetime import datetime

# Login Page
def LoginPage(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username_in = request.POST['username']
            password_in = request.POST['password']
            verify_user = CustomUser.objects.get(username=username_in)
            user = authenticate(username = username_in, password = password_in)
            if user is not None:
                otp = request.POST['otp']
                if otp == '':
                    account_sid = os.environ['TWILIO_ACCOUNT_SID']
                    auth_token = os.environ['TWILIO_AUTH_TOKEN']
                    client = Client(account_sid, auth_token)
                    generate = random.randint(1000, 9999)
                    message = client.messages.create(
                                                body= str(generate),
                                                from_='+16204593952', 
                                                to='+917760131002'
                                            )

                    print(message.sid)
                    verify_user.otp = generate
                    verify_user.save()                
                    return render(request, 'usersite/login.html', {'username':username_in, 'password':password_in})
                elif otp == verify_user.otp:
                    login(request, user)
                    return redirect('user-home')
            else:
                messages.success(request, ("Invalid Username or Password"))
                return redirect('user-login')
        else:
            return render(request,'usersite/login.html')
    else:
        return render(request, 'usersite/index.html')

def SignupPage(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username_in = request.POST['username']
            if not username_in == '' :
                if not CustomUser.objects.filter(username = username_in):
                    email_in = request.POST['email']
                    if not CustomUser.objects.filter(email = email_in):
                        firstname_in = request.POST['first_name']
                        lastname_in = request.POST['last_name']
                        number_in = request.POST['phone_number']
                        if number_in == '' or not CustomUser.objects.filter(phone_number = number_in):
                            if request.POST['password1'] == request.POST['password2'] and not request.POST['password1']  == '':
                                password_in = request.POST['password1']
                                user_entery = CustomUser.objects.create_user(username = username_in,email = email_in,password = password_in, phone_number=number_in)
                                user_entery.first_name = firstname_in
                                user_entery.last_name = lastname_in
                                user_entery.save()
                                checked = request.POST.get('checked')
                                if checked: 
                                    user = authenticate(ussername = username_in, password = password_in)
                                    if user is not None:
                                        login(request, user)
                                        return redirect(request, 'user-home')
                                    else:
                                        messages.success(request, ("Registered successfully"))
                                        return redirect('user-login')
                                else:
                                    messages.success(request, ("Registered successfully"))
                                    return redirect('user-login')
                            else:
                                messages.success(request, ("Password does not match"))
                                return render(request, 'usersite/signup.html')
                        else:
                            messages.success(request, ("Invalid Phone or already exists"))
                            return redirect('user-login')
                    else:
                        messages.success(request, ("Email already exist"))
                        return render(request, 'usersite/signup.html')
                else:
                    messages.success(request, ("Username already exist"))
                    return redirect('user-signup')
            else:
                messages.success(request, ("Username must be provided"))
                return render(request, 'usersite/signup.html')
            
        else:
            return render(request, 'usersite/signup.html')  
    else:
        return render(request, 'usersite/index.html')

def HomePage(request):
    if request.method == 'POST':
        try:
            searched = request.POST['user_searched']
            products = Products.objects.filter(title__contains=searched)
            categories = Categories.objects.all()
        except:
            redirect('user-home')
        return render(request, 'usersite/searchproduct.html', {'products':products, 'categories':categories})
        

    else:
        products = Products.objects.all()
        categories = Categories.objects.all()
        orders = Order.objects.all()
        try:
            count = OrderItem.objects.filter(user = request.user, ordered=False).count()
        except:
            count = 0
        context = {'products':products, 'categories':categories, 'orders':orders, 'count':count}
        return render(request, 'usersite/index.html', context)

def LogoutUser(request):
    logout(request)
    messages.success(request, ("Loged out successfuly"))
    return redirect('user-home')

def user_profile(request):
    user = request.user
    user_info = CustomUser.objects.get(username=user)
    try:
        user_address = Address.objects.get(user = user_info.id)
        categories = Categories.objects.all()
    except:
        user_address = None
    user_orders = Order.objects.filter(user=user, ordered = True)
    context = {'user_info':user_info, 'user_address':user_address, 'user_orders':user_orders, 'categories':categories}
    return render(request, 'usersite/user-profile.html', context)

def user_edit(request):
    user = request.user.id
    try:
        address = Address.objects.get(user=user)
        categories = Categories.objects.all()
    except:
        address = Address.objects.create(user=user)
    user_details = CustomUser.objects.get(id = user)
    user_form = UsersideEditForm(request.POST or None, instance=user_details)
    user_address = AddressForm(request.POST or None, instance=address)
    context = {"user_form":user_form, "user_address":user_address, 'categories':categories}
    if user_form.is_valid() and user_address.is_valid():
        user_form.save()
    if user_address.is_valid():
        user_address.save()
        return redirect('user-profile')
    return render(request, "usersite/edit-profile.html", context)

def user_password(request):
    user = request.user.id
    customer = CustomUser.objects.get(id = user)
    categories = Categories.objects.all()
    if request.method == "POST":
        if request.POST['password1'] == request.POST['password2']:
            customer.set_password = request.POST['password1']
            customer.save()
            return redirect('user-profile')
        else:
            messages.success(request,"Password does not match")
            return render(request, 'usersite/password.html', {'categories':categories})
    else:
        return render(request, 'usersite/password.html',{'categories':categories})

def view_product(request, product_id):
    product = Products.objects.get(id=product_id)
    categories = Categories.objects.all()
    context = {'product':product, 'categories':categories}
    return render(request, 'usersite/productdetail.html', context)

def category_product(request,category_id):
    products = Products.objects.filter(category=category_id)
    category_name = Categories.objects.get(id = category_id)
    categories = Categories.objects.all()
    return render(request, 'usersite/category-wise.html', {'products':products, 'category_name':category_name, 'categories':categories})


def cart(request):
    if request.user.is_authenticated:
        try:
            user = request.user
            items = OrderItem.objects.filter(user=user, ordered=False)
            cart = items[0]
        except:
            cart = None
    else:
        return redirect('user-login')
    if request.method == "POST":
        try:
            if request.POST['cancel'] == 'on':
                del request.session['coupon_id']
                messages.success(request, 'Coupon Removed')
                return redirect('cart')
        except:
            now = datetime.now()
            form = CouponUserForm(request.POST)
            code = request.POST['code']
            try:
                coupon = Coupon.objects.get(code__iexact=code, valid_from__lte=now, valid_to__gte=now, active=True)
                request.session['coupon_id'] = coupon.id
                print('here')
                messages.success(request, 'Coupon Applied')
                return redirect('cart')
            except:
                messages.error(request, 'Coupon Not Exists')
                return redirect('cart')
    form = CouponUserForm()
    if 'coupon_id' in request.session and cart is not None:
        discount = Coupon.objects.get(id = request.session['coupon_id'] ).discount
        discount_price = (cart.get_cart_total * discount)/100
        total_discount = cart.get_cart_total - discount_price  
    else:
        discount_price = 0
        if cart is not None:
            total_discount = cart.get_cart_total
        else:
            total_discount = 0
    categories = Categories.objects.all()
    context = {'items':items, 'cart':cart, 'categories':categories, 'form':form ,'discount':discount_price , 'total_discount':total_discount}
    return render(request, 'usersite/cart.html', context)


def checkout(request):
    
    if request.user.is_authenticated:
        user = CustomUser.objects.get(username = request.user)
        items = OrderItem.objects.filter(user=user, ordered=False)
        if not items:
            return redirect('user-home')
    address,create = Address.objects.get_or_create(user=user)
    address.save()
    form = AddressForm(request.POST or None, instance=address)
    if request.method == 'POST':
        if form.is_valid:
            form.user = user.id
            form.save()
            return redirect('payment')
        
    else:
        items = []
    context = {'items':items, 'form':form}
    return render(request, 'usersite/checkout.html', context)

def contact(request):
    return render(request, 'usersite/contact.html')


def update_product(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    custumer = CustomUser.objects.get(username=request.user)
    product = Products.objects.get(id=productId)
    orderItem, create = OrderItem.objects.get_or_create(user=custumer, item=product, ordered=False)
    if (product.current_stock - orderItem.quantity) <= 0 :
        if action == 'sub':
            orderItem.quantity = (orderItem.quantity - 1)
        orderItem.save()
        if orderItem.quantity <= 0 or action == 'remove':
            orderItem.delete()
        return JsonResponse("item added", safe=False)
    else:
        if action == 'add':
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == 'sub':
            orderItem.quantity = (orderItem.quantity - 1)
        orderItem.save()
        if orderItem.quantity <= 0 or action == 'remove':
            orderItem.delete()

    

def payment(request):
    user = request.user
    items = OrderItem.objects.filter(user=user, ordered=False)
    if not items:
        return redirect('user-home')
    cart = items[0]
    try:
        discount = Coupon.objects.get(id = request.session['coupon_id'] ).discount
        discount_price = (cart.get_cart_total*discount)/100
        total_discount = cart.get_cart_total - discount_price
    except:
        discount_price = 0
        total_discount = cart.get_cart_total
    try:
        # orderitems = OrderItem.objects.filter(user = user, ordered=False)
        # order_items_total = orderitems[0]
        amount = total_discount * 100
        client = razorpay.Client(auth=("rzp_test_RZFc4u0eaLbvd0", "7uVteAfcqZTeF9Jct9OBRn3a"))
        client.set_app_details({"title" : "Shipit", "version" : "1.0.00."})
        payment = client.order.create({"amount": amount, "currency": "INR", "payment_capture":"1"})
    except:
        amount = 0
        payment = None
    if request.method == 'POST':
        try:
            cod = request.POST['cod']
        except:
            cod = ''
        if cod == 'on':
            order = Order.objects.create(user = user)
            orderitems = OrderItem.objects.filter(user = user, ordered=False)
            if not orderitems:
                return redirect('user-home')
            for orderitem in orderitems:
                order.items.add(orderitem.id)
                orderitem.ordered = True
                orderitem.save()
            order.shipping_address = Address.objects.get(user=user)
            order.billing_address = Address.objects.get(user=user)
            order.ordered=True
            order.transaction_status = 'COD'
            order.save()
            return redirect('ordered')
        elif json.loads(request.body):
            data = json.loads(request.body)
            if data['transaction_status'] == 'COMPLETED':
                print(data['transaction_status'])
                transfer_status = data['transaction_status']
                transfer_id = data['transaction_id']
                order = Order.objects.create(user = user)
                orderitems = OrderItem.objects.filter(user = user, ordered=False)
                if not orderitems:
                    return redirect('user-home')
                for orderitem in orderitems:
                    order.items.add(orderitem.id)
                    orderitem.ordered = True
                    orderitem.save()
                order.shipping_address = Address.objects.get(user=user)
                order.billing_address = Address.objects.get(user=user)
                order.ordered=True
                order.transaction_status = transfer_status
                order.transaction_id = transfer_id
                order.save()
                return redirect('ordered')
            elif data['transaction_status'] is not None:
                print(data['transaction_status'])
                transfer_status = data['transaction_id']
                transfer_id = data['transaction_status']
                order = Order.objects.create(user = user)
                orderitems = OrderItem.objects.filter(user = user, ordered=False)
                if not orderitems:
                    return redirect('user-home')
                for orderitem in orderitems:
                    order.items.add(orderitem.id)
                    orderitem.ordered = True
                    orderitem.save()
                order.shipping_address = Address.objects.get(user=user)
                order.billing_address = Address.objects.get(user=user)
                order.ordered=True
                order.transaction_status = transfer_status
                order.transaction_id = transfer_id
                order.save()
                return redirect('ordered')
            else:
                return redirect('payment')
        else:
            return redirect('payment')
    elif request.user.is_authenticated:
        usd = int(total_discount/50)
        context = {'items':items, 'payment':payment, 'amount':amount, 'discount':discount_price,
         'total_discount':total_discount, 'usd':usd}
        return render(request, 'usersite/payment.html', context)
    else:
        items = []
        usd = 0
        context = {'items':items,'usd':usd, 'payment':payment, 'amount':amount, 'discount':discount_price, 'total_discount':total_discount}
        return render(request, 'usersite/payment.html', context)
    
def place_order(request):
    return render(request, 'usersite/orderplaced.html')

def orders(request):
    try:
        orders = Order.objects.filter(user=request.user).order_by('-id')
    except:
        orders = None
    date = datetime.now()
    categories = Categories.objects.all()
    return render(request, 'usersite/order.html' , {'categories':categories, 'orders':orders,'date':date })

def orders_cancel(requset, order_id):
    order = Order.objects.get(id=order_id)
    order.cancel = True
    order.save()
    return redirect('user-orders')

def return_order(request, order_id):
    order = Order.objects.get(id = order_id)
    order.returning = True
    order.save()
    print(order.returning)
    return redirect('user-orders') 