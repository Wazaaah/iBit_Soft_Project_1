from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from marketplacepro.forms import ProductForm
from marketplacepro.models import Product, Cart, CartItem, ShopBalance


# Create your views here.
def index(request):
    return render(request, 'index.html')


def shop(request):
    products = Product.objects.all()
    return render(request, 'shop.html', {'products': products})


def contact(request):
    return render(request, 'contact.html')


def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart.items.all())

    context = {
        'cart': cart,
        'total_price': total_price
    }

    return render(request, 'checkout.html', context)


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


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Check if the product is in stock
    if product.stock > 0:
        # Get the user's cart or create one if it doesn't exist
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if the cart already has this product
        cart_item, created = CartItem.objects.get_or_create(product=product)

        if not created:
            # If the item already exists in the cart, increase the quantity
            cart_item.quantity += 1
        else:
            # If the item is newly created, set the quantity to 1
            cart_item.quantity = 1

        cart_item.save()

        # Add the cart item to the user's cart
        cart.items.add(cart_item)

        # Reduce the product stock
        product.stock -= 1
        product.save()

        messages.success(request, f'Added {product.name} to your cart.')
    else:
        messages.error(request, f'Sorry, {product.name} is out of stock.')

    return redirect('shop')


def cart_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    return render(request, 'cart.html', {'cart': cart})


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    # Increase the stock when an item is removed
    product = cart_item.product
    product.stock += cart_item.quantity
    product.save()

    cart_item.delete()
    return redirect('cart_view')


def place_order(request):
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart.items.all())

        # Get the user's balance
        shop_balance = get_object_or_404(ShopBalance, user=request.user)

        if shop_balance.balance >= total_price:
            # Deduct the amount from the shop balance
            shop_balance.balance -= total_price
            shop_balance.save()

            # Clear the cart
            cart.items.all().delete()
            return redirect('thankyou')  # Redirect to a thank you or order confirmation page
        else:
            messages.error(request, 'Insufficient balance to place the order.')

    return redirect('checkout')

#To generate report on products purchased
def purchase_report(request):
    
    checkouts = Checkout.objects.all()

    report_data = []
    for checkout in checkouts:

        cart_items = CartItem.objects.filter(carts_checkout=checkout)

        for item in cart_items:
            report_data.append({
               'user': checkout.user.username,
                'product_name': item.product.name,
                'category': item.product.category,
                'price': item.product.price,
                'quantity': item.quantity,
                'total_price': item.quantity * item.product.price,
                'checkout_date': checkout.checkout_date 
            })
    return render(request, 'purchase_report.html', {'report_data': report_data})
            
