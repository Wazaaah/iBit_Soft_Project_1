from django.contrib import admin
from .models import Product, Cart, CartItem, Checkout, ShopBalance, CheckoutItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity')
    search_fields = ('product__name',)
    list_filter = ('product',)


@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'checkout_date')
    list_filter = ('checkout_date',)
    search_fields = ('user__username',)
    ordering = ('-checkout_date',)


@admin.register(ShopBalance)
class ShopBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__username',)
    ordering = ('-updated_at',)


@admin.register(CheckoutItem)
class CheckoutItemAdmin(admin.ModelAdmin):
    list_display = ('checkout', 'product', 'quantity', 'price', 'date')

