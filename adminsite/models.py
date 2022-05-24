from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

from pytz import UTC
ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
    ('D', 'Both')
)
class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=13, unique=True)
    otp = models.CharField(max_length=4, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to = 'uploaded/profile')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELD = []


    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = 'https://bootdey.com/img/Content/avatar/avatar7.png'
        return url
        


class Categories(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    

class Products(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    stock = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    description = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to = 'product')

    def __str__(self):
        return self.title

    

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    @property
    def current_stock(self):
        ordered_quantity = self.orderitem_set.all()
        total_ordered_quantity = sum([quantity.quantity for quantity in ordered_quantity if quantity.ordered])
        stock_existing = self.stock - total_ordered_quantity
        return stock_existing

    @property
    def offer_price(self):
        category = self.category
        try:
            category_offer = category.categoryoffer_set.get(category=category.id, active=True)
            category_offer = category_offer.discount
        except:
            category_offer = 0
        try:
            product_offer = self.productoffer_set.get(product=self.id, active=True)
            product_offer = product_offer.discount
        except:
            product_offer = 0
        
        if category_offer <= product_offer:
            offer_price = self.price - (product_offer * self.price) / 100
        elif category_offer >= product_offer:
            offer_price = self.price - (category_offer * self.price) / 100
        else:
            offer_price = self.price
        return offer_price

    @property
    def offer(self):
        category = self.category
        try:
            category_offer = category.categoryoffer_set.get(category=category.id, active=True)
            category_offer = category_offer.discount
        except:
            category_offer = 0
        try:
            product_offer = self.productoffer_set.get(product=self.id, active=True)
            product_offer = product_offer.discount
        except:
            product_offer = 0
        
        if category_offer <= product_offer:
            offer = product_offer
        elif category_offer >= product_offer:
            offer = category_offer
        else:
            offer = 0
        return offer

class OrderItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    @property
    def get_total(self):
        total = self.item.offer_price * self.quantity
        return total

    @property
    def get_cart_total(self):
        order_total = self.user.orderitem_set.all()
        total = sum([item.get_total for item in order_total if not item.ordered])
        return total

    @property
    def get_cart_total_in_dollor(self):
        order_total = self.user.orderitem_set.all()
        total = sum([item.get_total for item in order_total if not item.ordered])
        return total/60


    @property
    def get_cart_items(self):
        order_total = self.user.orderitem_set.all()
        total = sum([item.quantity for item in order_total if not item.ordered])
        return total


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey('Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    conformed = models.BooleanField(default=True, null=True, blank=True)
    shiped = models.BooleanField(default=False, null=True, blank=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    cancel = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=50, null=True, blank=True)
    transaction_status = models.CharField(max_length=50, null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    returning = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    @property
    def get_ordered_total(self):
        order_total = self.items.all()
        total = sum([item.get_total for item in order_total if item.ordered])
        return total

    @property
    def returnable(self):
        now = self.delivery_date
        check_date = datetime.datetime.now(UTC)
        if now is not None:
            till = self.delivery_date + datetime.timedelta(days=10)
            if till > check_date:
                return till
            else:
                return False
        else:
            return False

    

class Address(models.Model):
    user = models.ForeignKey(CustomUser,null=True, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.username)


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    active = models.BooleanField()

    def __str__(self):
        return self.code

class CategoryOffer(models.Model):
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    active = models.BooleanField()

    def __str__(self):
        return self.category.name


class ProductOffer(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    active = models.BooleanField()

    def __str__(self):
        return self.product.title
