from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('shop', views.shop, name='shop'),
    path('contact', views.contact, name='contact'),
    path('checkout', views.checkout, name='checkout'),
    path('thankyou', views.thankyou, name='thankyou'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('upload_product', views.upload_product, name='upload_product'),
    path('admin_options', views.admin_options, name='admin_options'),
    path('view_products', views.view_products, name='view_products'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

]
