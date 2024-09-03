from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'index.html')


def shop(request):
    return render(request, 'shop.html')


def contact(request):
    return render(request, 'contact.html')


def cart(request):
    return render(request, 'cart.html')


def checkout(request):
    return render(request, 'checkout.html')


def thankyou(request):
    return render(request, 'thankyou.html')


def login(request):
    return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')