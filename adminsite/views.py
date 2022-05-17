from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Categories, Products, Address, Order, CustomUser
from .forms import *
import datetime
from django.contrib.auth.decorators import user_passes_test

#csv imports
import csv


#  PDF imports
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

# ADMIN SIDE LOGIN
def admin_login(request):
    if not request.user.is_superuser or request.user.is_staff:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username = username, password = password)
            if user is not None:
                login(request, user)
                messages.success(request, ("Loged in successfully"))
                return redirect('admin_home')
            else:
                messages.success(request, ("Invalid username or password"))
                return redirect('admin_login')
        else:
            return render(request, 'adminsite/login.html')
    else:
        return redirect('admin_home')


#ADMIN SIDE HOMEPAGE
@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def home_page(request):
    if request.user.is_superuser or request.user.is_staff:
        user_count = CustomUser.objects.all()
        order_count = Order.objects.all()
        product_count = Products.objects.all()
        category_count = Categories.objects.all()
        today = datetime.date.today()
        today_order = Order.objects.filter(ordered_date__date = today)
        month = today.month
        this_month_order = Order.objects.filter(ordered_date__month = month)
        last_month_order = Order.objects.filter(ordered_date__month = (month-1))
        year = today.year
        this_year_order = Order.objects.filter(ordered_date__year = year)
        last_year_order = Order.objects.filter(ordered_date__year = (year-1))
        cod = Order.objects.filter(transaction_status = "COD")
        paypal = Order.objects.filter(transaction_status = "COMPLETED")
        razorpay = Order.objects.filter(transaction_status__contains = "_")
        context = {'cod':cod,'paypal':paypal,'razorpay':razorpay, 'user': user_count, 'order': order_count, 'product': product_count, 'category': category_count,'last_month_order':last_month_order, 'today_order':today_order, 'this_month_order':this_month_order, 'this_year_order':this_year_order,'last_year_order':last_year_order}
        return render(request, 'adminsite/index.html', context)
    else:
        return redirect('admin_login')

#ADMIN SIDE CHART GENERATION
@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def chart_details(request):
    user_chart = CustomUser.objects.all().values()
    order_chart = Order.objects.all().values()
    product_chart = Products.objects.all().values()
    category_chart = Categories.objects.all().values()
    data = {'category_chart':list(category_chart), 'user_chart':list(user_chart), 'order_chart':list(order_chart), 'product_chart':list(product_chart)}
    return JsonResponse(data)
    

def admin_logout(request):
    logout(request)
    messages.success(request, "Loged out successfully")
    return redirect('admin_login')


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def list_users(request):
    users = CustomUser.objects.all()
    return render(request, 'adminsite/users.html',{'user_page':users})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def view_users(request, user_id):
    user = CustomUser.objects.get(pk=user_id)
    try:
        address = Address.objects.get(user=user.id)
    except :
        return render(request, 'adminsite/user-view.html', {'user': user})
    return render(request, 'adminsite/user-view.html', {'user': user, 'address':address})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def block_user(request, user_id):
    user = CustomUser.objects.get(pk = user_id)
    user.is_active = False
    user.save()
    return redirect('users')


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def unblock_user(request, user_id):
    user = CustomUser.objects.get(pk = user_id)
    user.is_active = True
    user.save()
    return redirect('users')


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def list_categories(request):
    categories = Categories.objects.all()
    return render(request, 'adminsite/categories.html', {'categories_page': categories})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def view_categories(request, categories_id):
    categorie = Categories.objects.get(id=categories_id)
    return render(request, 'adminsite/categories_view.html',{'categorie':categorie})
    

@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def delete_categories(request, categories_id):
        Categories.objects.filter(pk=categories_id).delete()
        return redirect('categories')


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def add_categories(request):
    if request.method == 'POST':
        form = CategoriesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        form = CategoriesForm
        title = 'Add Categories'
        return render(request, 'adminsite/add-category.html', {'form':form, 'title':title})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def edit_categories(request, categories_id):
    category=Categories.objects.get(id=categories_id)
    form = CategoriesForm(request.POST or None, instance=category)
    if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        title = 'Edit Categories'
        form = CategoriesForm(instance=category)
        return render(request, 'adminsite/edit-category.html', {'form':form, 'title':title})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def list_products(request):
    products = Products.objects.all()
    return render(request, 'adminsite/products.html',{'products': products})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def view_products(request, products_id):
    products = Products.objects.get(id=products_id)
    return render(request, 'adminsite/categories_view.html',{'products':products})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def delete_products(request, products_id):
    Products.objects.filter(id=products_id).delete()
    return redirect('products')


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def add_products(request):
    if request.method == 'POST':
        form = ProductsForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect('products')
        else:
            return redirect('add_products')
    else:
        form = ProductsForm
        return render(request, 'adminsite/add-product.html', {'form':form})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def edit_products(request, products_id):
    category=Products.objects.get(id=products_id)
    form = ProductsForm(request.POST or None, request.FILES or None, instance=category)
    if form.is_valid():
            form.save()
            return redirect('products')
    else:
        title = 'Edit Product'
        form = ProductsForm(instance=category)
        context = {'form':form, 'title':title, 'category':category}
        return render(request, 'adminsite/edit-product.html', context)


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def list_orders(request):
    order_filter = Order.objects.all()
    title = 'Orders'
    return render(request, 'adminsite/orders.html',{'orders': order_filter, 'title':title, 'order_filter':order_filter,})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def view_orders(request, orders_id):
    order = Order.objects.get(id=orders_id)
    order_item = order.items.all()
    address = Address.objects.get(user=order.user.id)
    return render(request, 'adminsite/order-view.html', {'order':order, 'order_items':order_item, 'address':address})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def edit_orders(request, orders_id):
    category=Order.objects.get(id=orders_id)
    form = OrderForm(request.POST or None, request.FILES or None, instance=category)
    if form.is_valid():
            form.save()
            return redirect('orders')
    else:
        title = 'Edit order'
        form = OrderForm(instance=category)
        return render(request, 'adminsite/edit-order.html', {'form':form, 'title':title, 'category':category})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def admin_order_cancel(requset, orders_id):
    order = Order.objects.get(id=orders_id)
    if order.cancel:
        order.cancel = False
        order.save()
        return redirect('orders')
    else:
        order.cancel = True
        order.save()
        return redirect('orders')


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def search(request):
    if request.method == 'POST':
        if request.POST['search'] == '':
            return redirect('admin_home')
        search = request.POST['search']
        print(search)
    users = CustomUser.objects.filter(username__contains = search)
    categories = Categories.objects.filter(name__contains = search)
    products = Products.objects.filter(title__contains = search)
    context = {'users':users, 'categories':categories, 'products':products}
    return render(request, 'adminsite/search.html', context)


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def reports(request):
    month = datetime.date.today().month
    year = datetime.date.today().year
    total = Order.objects.filter(ordered_date__month = month, ordered_date__year = year, cancel=False, returning=False)
    all_total = Order.objects.all()
    all_amount = all_total.filter(cancel=False, returning=False)
    all_order = all_total.count
    return_order = all_total.filter(returning=True).count
    cancel_order = all_total.filter(cancel=True).count
    by_month = total.count
    total_amount = 0
    all_total_amount = 0
    total_refund = all_total.exclude(cancel=False, returning = False, transaction_status = 'COD')
    refund = 0
    for x in total:
        total_amount += x.get_ordered_total
    for x in all_amount:
        all_total_amount += x.get_ordered_total
    for x in total_refund:
        refund += x.get_ordered_total
    context = {'total_amount': total_amount,'by_month':by_month, 'all_total_amount':all_total_amount,
     'all_order':all_order, 'return_order':return_order, 'cancel_order':cancel_order, 'refund':refund}
    return render(request, 'adminsite/reports.html', context)


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def report_genretor(request):
    if  request.GET['report_type'] == 'excel':
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(request.GET['report_on'])

        #writer
        if request.GET['report_on'] == 'products':
            if request.GET['name']:
                orders = Products.objects.filter(title__contains = request.GET['name'])
            else:
                orders = Products.objects.all()
            writer = csv.writer(response)
            writer.writerow(['TITLE','PRICE','STOKE', 'CATEGORY', 'TOTAL SALES', 'TOTAL SALES AMOUNT'])
            for order in orders:
                stock = order.stock - order.current_stock
                total_amount = stock * order.price
                writer.writerow([order.title, order.price, order.current_stock, order.category, stock, total_amount ])
            return response

        elif request.GET['report_on'] == 'order':
            if request.GET['from'] and request.GET['to']:
                orders = Order.objects.filter(ordered_date__range = [request.GET['from'], request.GET['to']])
            elif request.GET['from']:
                orders = Order.objects.filter(ordered_date__range = [request.GET['from']])
            elif request.GET['to']:
                orders = Order.objects.filter(ordered_date__contains = request.GET['to'])
            else:
                orders =Order.objects.all()
            if request.GET['day']:
                orders = Order.objects.filter(ordered_date__contains = request.GET['day'])
            writer = csv.writer(response)
            writer.writerow(['ORDER ID','ITEMS','QUANTITY', 'ORDER DATE','TOTAL PRICE' 'ADDRESS'])
            for order in orders:
                items = [order_item.item.title for order_item in order.items.all()]
                quantity = [item_quantity.quantity for item_quantity in order.items.all()]
                address = [order.billing_address.street_address, order.billing_address.apartment_address, order.billing_address.country, order.billing_address.zip]
                writer.writerow([order.id, str(items)[1:-1], str(quantity)[1:-1], order.ordered_date, order.get_ordered_total, str(address)[1:-1]])
            return response
        
    elif request.GET['report_type'] == 'pdf':
        # Create Bytestream buffer
        buf = io.BytesIO()
        # Create a canvas
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        print(canvas)
        # Text object
        textob = c.beginText()
        textob.setTextOrigin(inch,inch)
        textob.setFont("Helvetica", 14)

        # Adding lines of Text
        if request.GET['report_on'] == 'products':
            if request.GET['name']:
                orders = Products.objects.filter(title__contains = request.GET['name'])
            else:
                orders = Products.objects.all()

            for order in orders:
                stock = order.stock - order.current_stock
                total_amount = stock * order.price
                writer = (['TITLE : '+str(order.title),'PRICE : '+str(order.price), 'STOKE : '+str(order.current_stock), 'CATEGORY : '+ str(order.category), 'TOTAL SALES : '+str(stock), 'TOTAL SALES AMOUNT : '+str(total_amount) ])
                for line in writer:
                    textob.textLine(line)
                    textob.textLine("============================================================")
                textob.textLine("")
                textob.textLine("")
            c.drawText(textob)
            c.showPage()
            c.save()
            buf.seek(0)
            # Return PDF
            if request.GET['name']:
                name = request.GET['name']
                return FileResponse(buf, as_attachment=True, filename='{}.pdf'.format(name))
            else:
                return FileResponse(buf, as_attachment=True, filename='all_product.pdf')
        else:
            textob = c.beginText()
            textob.setTextOrigin(inch,inch)
            textob.setFont("Helvetica", 14)
            if request.GET['from'] and request.GET['to']:
                orders = Order.objects.filter(ordered_date__range = [request.GET['from'], request.GET['to']])
            elif request.GET['from']:
                orders = Order.objects.filter(ordered_date__range = [request.GET['from']])
            elif request.GET['to']:
                orders = Order.objects.filter(ordered_date__contains = request.GET['to'])
            else:
                orders =Order.objects.all()
            print(orders)
            if request.GET['day']:
                orders = Order.objects.filter(ordered_date__contains = request.GET['day'])
            # (['ORDER ID','ITEMS','QUANTITY', 'ORDER DATE','TOTAL PRICE' 'ADDRESS'])
            print(orders)
            for order in orders:
                items = [order_item.item.title for order_item in order.items.all()]
                quantity = [item_quantity.quantity for item_quantity in order.items.all()]
                address = [order.billing_address.street_address, order.billing_address.apartment_address, order.billing_address.country, order.billing_address.zip]
                writers = (['ORDER ID : '+ str(order.id), 'ITEMS : '+ str(items)[1:-1], 'QUANTITY : '+str(quantity)[1:-1], 'ORDER DATE : '+str(order.ordered_date), 'TOTAL PRICE : '+str(order.get_ordered_total), 'ADDRESS : '+str(address)[1:-1]])
                print(writers)
                for lines in writers:
                    textob.textLine(lines)
                    textob.textLine("--------------------------------------------------------------")
                textob.textLine("")
                textob.textLine('===============================================================')

            c.drawText(textob)
            c.showPage()
            c.save()
            buf.seek(0)
            # Return PDF
            return FileResponse(buf, as_attachment=True, filename='product.pdf')
    else:
        return redirect('reports')


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def offers(request):
    coupons = Coupon.objects.all()
    category_off = CategoryOffer.objects.all()
    product_off = ProductOffer.objects.all()
    context = {'coupons':coupons, 'category_off':category_off, 'product_off':product_off}
    return render(request, 'adminsite/offers.html', context)


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def coupon_view(request, coupon_id):
    coupon = Coupon.objects.get(id = coupon_id)
    return render(request, 'adminsite/coupon-view.html', {'coupon':coupon})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def coupon_add(request):
    title = 'Adding Coupon Offer'
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid:
            form.save()
            return redirect('offers')
        else:
            return redirect('coupon_add')
    else:
        form = CouponForm
        return render(request, 'adminsite/add-offer.html',{'form':form, 'title':title})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def coupon_edit(request, coupon_id):
    title = 'Editing Coupon Offer'
    coupon_exist = Coupon.objects.get(id = coupon_id)
    if request.method == 'POST':
        form = CouponForm(request.POST or None, instance=coupon_exist)
        if form.is_valid:
            form.save()
            return redirect('offers')
        else:
            return redirect('category_offer_add')
    else:
        form = CouponForm(instance=coupon_exist)
        return render(request, 'adminsite/add-offer.html',{'form':form, 'title':title})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def coupon_delete(request, coupon_id):
    Coupon.objects.filter(id=coupon_id).delete()
    return redirect('offers')
    

@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def category_offer_view(request, category_id):
    category = CategoryOffer.objects.get(id = category_id)
    return render(request, 'adminsite/category-off.html', {'category':category})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def category_offer_add(request):
    title = 'Adding Category Offer'
    if request.method == 'POST':
        form = CategoryOffForm(request.POST)
        if form.is_valid:
            form.save()
            return redirect('offers')
        else:
            return redirect('category_offer_add')
    else:
        form = CategoryOffForm
        return render(request, 'adminsite/add-offer.html',{'form':form, 'title':title})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def category_offer_edit(request, category_id):
    title = 'Editing Category Offer'
    cat_exist = CategoryOffer.objects.get(id = category_id)
    if request.method == 'POST':
        form = CategoryOffForm(request.POST or None, instance=cat_exist)
        if form.is_valid:
            form.save()
            return redirect('offers')
        else:
            return redirect('category_offer_add')
    else:
        form = CategoryOffForm(instance=cat_exist)
        return render(request, 'adminsite/add-offer.html',{'form':form, 'title':title})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def category_offer_delete(request, category_id):
    CategoryOffer.objects.filter(id=category_id).delete()
    return redirect('offers')


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def product_offer_view(request, product_id):
    product = ProductOffer.objects.get(id = product_id)
    return render(request, 'adminsite/product-off.html', {'product':product})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def product_offer_add(request):
    title = 'Adding Product Offer'
    if request.method == 'POST':
        form = ProductOffForm(request.POST)
        if form.is_valid:
            form.save()
            return redirect('offers')
        else:
            return redirect('category_offer_add')
    else:
        form = ProductOffForm
        return render(request, 'adminsite/add-offer.html',{'form':form, 'title':title})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def product_offer_edit(request, product_id):
    title = 'Editing Product Offer'
    pro_exist = ProductOffer.objects.get(id = product_id)
    if request.method == 'POST':
        form = ProductOffForm(request.POST or None, instance=pro_exist)
        if form.is_valid:
            form.save()
            return redirect('offers')
        else:
            return redirect('category_offer_add')
    else:
        form = ProductOffForm(instance=pro_exist)
        return render(request, 'adminsite/add-offer.html',{'form':form, 'title':title})


@user_passes_test(lambda u: u.is_superuser,login_url="admin_login")
def product_offer_delete(request, product_id):
    ProductOffer.objects.filter(id=product_id).delete()
    return redirect('offers')