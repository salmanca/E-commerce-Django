from django import forms
from django.forms import ModelForm
from .models import Categories, ProductOffer, Products, CategoryOffer, Address, Order, Coupon


class CategoriesForm(ModelForm):
    
    class Meta:
        model = Categories
        fields = '__all__'
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control'}),
        }
class ProductsForm(forms.ModelForm):
    
    class Meta:
        model = Products
        fields = '__all__'
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control'}),
            'price':forms.NumberInput(attrs={'class':'form-control'}),
            'stock':forms.NumberInput(attrs={'class':'form-control'}),
            'category':forms.Select(attrs={'class':'form-control'}),
            'description':forms.TextInput(attrs={'class':'form-control'}),
        }


class AddressForm(forms.ModelForm):
    
    class Meta:
        model = Address
        fields =('apartment_address', 'street_address', 'country', 'zip','default',)
        widgets = {
            'street_address':forms.TextInput(attrs={'class':'form-control'}),
            'apartment_address':forms.TextInput(attrs={'class':'form-control'}),
            'country':forms.TextInput(attrs={'class':'form-control'}),
            'zip':forms.NumberInput(attrs={'class':'form-control'}),
        }

class OrderForm(forms.ModelForm):
    
    class Meta:
        model = Order
        fields = ("conformed", "shiped", "received", "delivery_date")
        

class CouponUserForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ('code',)
        labels = {
            'code':'',
        }
        widgets = {
            'code':forms.TextInput(attrs={'class':'form-control m-2 p-4'}),
        }

class CouponForm(forms.ModelForm):
    active = forms.BooleanField( )
    class Meta:
        model = Coupon
        fields = '__all__'
        widgets = {
            'code':forms.TextInput(attrs={'class':'form-control m-2 p-4'}),
            'valid_from':forms.DateInput(attrs={'class':'form-control m-2 p-4'}),
            'valid_to':forms.DateInput(attrs={'class':'form-control m-2 p-4'}),
            'discount':forms.NumberInput(attrs={'class':'form-control m-2 p-4'}),
        }

class CategoryOffForm(forms.ModelForm):
    active = forms.BooleanField( )
    class Meta:
        model = CategoryOffer
        fields = '__all__'
        widgets = {
            'category':forms.Select(attrs={'class':'form-control m-2 p-4'}),
            'valid_from':forms.DateInput(attrs={'class':'form-control m-2 p-4'}),
            'valid_to':forms.DateInput(attrs={'class':'form-control m-2 p-4'}),
            'discount':forms.NumberInput(attrs={'class':'form-control m-2 p-4'}),
        }

class ProductOffForm(forms.ModelForm):
    active = forms.BooleanField( )
    class Meta:
        model = ProductOffer
        fields = '__all__'
        widgets = {
            'product':forms.Select(attrs={'class':'form-control m-2 p-4'}),
            'valid_from':forms.DateInput(attrs={'class':'form-control m-2 p-4'}),
            'valid_to':forms.DateInput(attrs={'class':'form-control m-2 p-4'}),
            'discount':forms.NumberInput(attrs={'class':'form-control m-2 p-4'}),
        }