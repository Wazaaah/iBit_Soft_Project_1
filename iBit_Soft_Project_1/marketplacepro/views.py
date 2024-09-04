from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, auth
from marketplacepro.forms import ProductForm
from marketplacepro.models import Product, Cart, CartItem, ShopBalance, Checkout, CheckoutItem
from django.utils import timezone
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from django.db.models import Sum
from django.shortcuts import render
import io
import urllib, base64


# Create your views here.
def index(request):
    products = Product.objects.all().order_by('?')
    # Limit to 3 random products
    products = products[:3]
    return render(request, 'index.html', {'products': products})


def shop(request):
    category_filter = request.GET.get('category')
    sort_by = request.GET.get('sort_by')

    # Filter by category if provided
    if category_filter:
        products = Product.objects.filter(category=category_filter)
    else:
        products = Product.objects.all()

    # Sort by price if specified
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('?')  # Random order as default

    # Get unique categories for filter dropdown
    categories = Product.objects.values_list('category', flat=True).distinct()

    # Get the number of items in the cart for the logged-in user
    try:
        cart = Cart.objects.get(user=request.user)
        cart_item_count = cart.items.aggregate(total_items=Sum('quantity'))['total_items'] or 0
    except Cart.DoesNotExist:
        cart_item_count = 0

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_filter,
        'selected_sort': sort_by,
        'cart_item_count': cart_item_count,
    }

    return render(request, 'shop.html', context)


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
            return redirect('/')
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
            # Create a Checkout entry
            checkout = Checkout.objects.create(
                user=request.user,
                total_price=total_price
            )

            # Save cart items to CheckoutItem
            for item in cart.items.all():
                CheckoutItem.objects.create(
                    checkout=checkout,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            # Deduct the amount from the shop balance
            shop_balance.balance -= total_price
            shop_balance.save()

            # Clear the cart
            cart.items.all().delete()

            return redirect('thankyou')  # Redirect to a thank you or order confirmation page
        else:
            messages.error(request, 'Insufficient balance to place the order.')

    return redirect('checkout')


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


def sales_trend_view(request):
    # Aggregate the total quantity sold at each exact timestamp
    sales_data = (
        CheckoutItem.objects
        .values('date')  # Use exact date and time
        .annotate(total_items_sold=Sum('quantity'))
        .order_by('date')
    )

    # Convert to a list of dictionaries
    data = list(sales_data)

    # Extract dates and quantities for plotting
    dates = [entry['date'] for entry in data]
    quantities = [entry['total_items_sold'] for entry in data]

    # Create the plot using Matplotlib
    plt.figure(figsize=(12, 8))  # Increase figure size for better visibility
    plt.plot(dates, quantities, marker='o', linestyle='-', color='dodgerblue', linewidth=2, markersize=8,
             markerfacecolor='orange')

    # Formatting the x-axis to show both date and time
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()  # Rotate date labels for better readability

    # Set titles and labels
    plt.title('Sales Trend by Exact Time', fontsize=20, fontweight='bold', color='darkblue')
    plt.xlabel('Date and Time', fontsize=14, color='darkblue')
    plt.ylabel('Total Items Sold', fontsize=14, color='darkblue')
    plt.grid(True, which='both', linestyle='--', linewidth=0.7, color='grey')

    # Set y-axis to show integers only (no decimals)
    plt.gca().yaxis.get_major_locator().set_params(integer=True)

    # Add a background color
    plt.gca().set_facecolor('#f7f7f7')

    # Customize the ticks on both axes
    plt.xticks(fontsize=12, color='darkblue')
    plt.yticks(fontsize=12, color='darkblue')

    # Add a legend
    plt.legend(['Total Items Sold'], loc='upper left', fontsize=12)

    # Save the plot to a string buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    return render(request, 'sales_trend.html', {'data': uri})


def sales_trend_view_today(request):
    # Define the specific day you want to filter by
    specific_day = timezone.now().date()  # For today, or you can specify a date

    # Aggregate the total quantity sold at each exact timestamp for that specific day
    sales_data = (
        CheckoutItem.objects
        .filter(date__date=specific_day)  # Filter by the specific day
        .values('date')
        .annotate(total_items_sold=Sum('quantity'))
        .order_by('date')
    )

    # Convert to a list of dictionaries
    data = list(sales_data)

    # Extract dates and quantities for plotting
    dates = [entry['date'] for entry in data]
    quantities = [entry['total_items_sold'] for entry in data]

    # Create the plot using Matplotlib
    plt.figure(figsize=(12, 8))
    plt.plot(dates, quantities, marker='o', linestyle='-', color='dodgerblue', linewidth=2, markersize=8,
             markerfacecolor='orange')

    # Formatting the x-axis to show both date and time
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()

    # Set titles and labels
    plt.title(f'Sales Trend for {specific_day}', fontsize=20, fontweight='bold', color='darkblue')
    plt.xlabel('Date and Time', fontsize=14, color='darkblue')
    plt.ylabel('Total Items Sold', fontsize=14, color='darkblue')
    plt.grid(True, which='both', linestyle='--', linewidth=0.7, color='grey')

    # Set y-axis to show integers only (no decimals)
    plt.gca().yaxis.get_major_locator().set_params(integer=True)

    # Add a background color
    plt.gca().set_facecolor('#f7f7f7')

    # Customize the ticks on both axes
    plt.xticks(fontsize=12, color='darkblue')
    plt.yticks(fontsize=12, color='darkblue')

    # Add a legend
    plt.legend(['Total Items Sold'], loc='upper left', fontsize=12)

    # Save the plot to a string buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    return render(request, 'sales_trend_today.html', {'data': uri})


def admin_options_2(request):
    return render(request, 'admin_options_2.html')


def report_for_today(request):
    today = timezone.now().date()
    records = CheckoutItem.objects.filter(date__date=today)  # Use __date to filter by just the date part

    main_records = []
    for record in records:
        main_records.append({
            'user': record.checkout.user.username,
            'product_name': record.product.name,
            'category': record.product.category,
            'price': record.price,  # Use record.price for the individual item price
            'quantity': record.quantity,
            'total_price': record.price * record.quantity,  # Calculate total price for the individual item
        })

    context = {
        'records': main_records
    }
    return render(request, "report_for_today.html", context)


def get_cart_count(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
        cart_count = cart.items.count()  # Adjust this based on your Cart model
    return JsonResponse({'cart_count': cart_count})
