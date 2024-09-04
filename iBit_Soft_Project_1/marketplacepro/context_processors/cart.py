# shop/context_processors/cart.py
from django.shortcuts import get_object_or_404
from marketplacepro.models import Cart


def cart_count(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
        cart_count = cart.items.count()  # Adjust based on your Cart model
    return {'cart_count': cart_count}
