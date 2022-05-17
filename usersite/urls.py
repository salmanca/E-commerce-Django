from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.HomePage, name = 'user-home'),
    path('login', views.LoginPage, name = 'user-login'),
    path('signup', views.SignupPage, name = 'user-signup'),
    path('category/<category_id>', views.category_product, name='category-product'),
    path('logout', views.LogoutUser, name='user-logout'),
    path('details/<product_id>', views.view_product, name='details'),
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('payment', views.payment, name='payment'),
    path('ordered', views.place_order, name='ordered'),
    path('update', views.update_product, name='update'),
    path('orders', views.orders, name='user-orders'),
    path('cancel/<order_id>', views.orders_cancel, name='cancel-orders'),
    path('return/<order_id>', views.return_order, name='return-orders'),
    path('profile', views.user_profile, name='user-profile'),
    path('edit', views.user_edit, name='user-edit'),
    path('change-password', views.user_password, name='user-password'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
