# shop/context_processors/cart.py
from django.shortcuts import get_object_or_404
from marketplacepro.models import Cart


def cart_count(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.items.count()
    return {'cart_count': cart_count}
