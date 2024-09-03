from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('shop', views.shop, name='shop'),
    path('contact', views.contact, name='contact'),
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('thankyou', views.thankyou, name='thankyou'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('upload_product', views.upload_product, name='upload_product'),
    path('admin_options', views.admin_options, name='admin_options'),
    path('view_products', views.view_products, name='view_products'),

]
