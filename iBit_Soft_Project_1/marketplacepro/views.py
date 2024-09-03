from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth

from marketplacepro.forms import ProductForm
from marketplacepro.models import Product


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
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/')  # Redirect to the home page or another page
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('register')

        # Create the user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        # Log the user in after registration
        auth_login(request, user)
        messages.success(request, f'Welcome {user.username}, your account has been created successfully!')
        return redirect('login')

    return render(request, 'register.html')


def logout(request):
    auth.logout(request)
    return redirect('/')


def upload_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_product')
    else:
        form = ProductForm()
    return render(request, 'upload_product.html', {'form': form})


def admin_options(request):
    return render(request, 'admin_options.html')


def view_products(request):
    products = Product.objects.all()
    return render(request, 'view_products.html', {'products': products})
