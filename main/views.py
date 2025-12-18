from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .models import Account, Product, Cart, Wishlist
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import date
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django import forms
from django.contrib.auth.decorators import login_required
import uuid
from yookassa import Configuration, Payment

def index(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'main/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Создаем пользователя
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'main/register.html', {'form': form})


def home(request):
    username = request.user.username
    if request.method == "POST":
        action = request.POST.get('action')
        if action =="add_to_cart":
            _id = request.POST.get('product_id')
            info = Product.objects.get(product_id=int(_id))
            if not Cart.objects.filter(product_id=_id, user=username).exists():
                new_product = Cart.objects.create(
                    title=info.title,
                    price=info.price,
                    image_url=info.image_url,
                    product_id=info.product_id,
                    count=1,
                    user=username
                )
            else:
                cart_item = Cart.objects.get(product_id=_id, user=username)
                cart_item.count += 1
                cart_item.save()
        elif action=="add_to_favorites":
            _id = request.POST.get('product_id')
            info = Product.objects.get(product_id=int(_id))
            if not Wishlist.objects.filter(product_id=_id, username=username).exists():
                new_wish= Wishlist.objects.create(
                    title=info.title,
                    price=info.price,
                    image_url=info.image_url,
                    product_id=info.product_id,
                    username=username
                )


    products = Product.objects.all()
    is_seller = request.user.groups.filter(name='seller').exists()
    return render(request, "main/home.html", {"products": products, "is_seller": is_seller})


def cart(request):
    username = request.user.username
    cart_items = Cart.objects.filter(user=username)
    for item in cart_items:
        item.total_price = item.price * item.count
    cart_total = sum([item.total_price for item in cart_items])

    context = {"cart_items": cart_items, "cart_total": cart_total}
    return render(request, "main/cart.html", context)

def create_payment(request):
    if request.method != "POST":
        return redirect('cart')
    Configuration.account_id = "1231470"
    Configuration.secret_key = "test_*gTYtsRnpfO4wf7d3m483knmfzPb0OkmFysy5UWPf6YqE"

    username = request.user.username
    cart_items = Cart.objects.filter(user=username)
    cart_total = sum(item.price * item.count for item in cart_items)

    amount_value = str(cart_total)

    idempotence_key = str(uuid.uuid4())
    try:
        payment = Payment.create({
            "amount": {
                "value": amount_value,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "http://127.0.0.1:8000/payment/success/"  # Полный URL
            },
            "capture": True,
            "description": f"Оплата корзины пользователя {username}"
        }, idempotence_key)
        return redirect(payment.confirmation.confirmation_url)

    except Exception as e:
        print(f"Ошибка создания платежа: {e}")
        return redirect('cart')

@login_required
def update_cart(request):
    username = request.user.username
    action = request.POST.get('action')
    product_id = request.POST.get('product_id')
    cart_item = Cart.objects.get(product_id=product_id, user=username)

    if action == 'plus':
        cart_item.count += 1
        cart_item.save()
    if action == 'minus':
        if cart_item.count > 1:
            cart_item.count -= 1
            cart_item.save()
        elif cart_item.count <= 1:
            cart_item.delete()
            return redirect('cart')

    return redirect('cart')


@login_required
def remove_from_cart(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        cart_items = Cart.objects.filter(product_id=product_id)
        cart_items.delete()
        return redirect('home/cart')

    return redirect('home/cart')


def exit(request):
    logout(request)
    return redirect('login')


@login_required
def product_detail(request, product_id):
    product =''
    context = {}
    return render(request, 'main/product_detail.html', context)


@login_required
def about(request):
    return render(request, 'main/about.html')


@login_required
def profile(request):
    wishlist_count = 0
    cart_items_count = 0
    username = request.user.username
    try:
        items = Cart.objects.filter(user=username)
        for item in items:
            cart_items_count += item.count
    except:
        pass
    user = request.user
    wishlist = Wishlist.objects.filter(username=username)
    for wish in wishlist:
        wishlist_count+=1
    return render(request, 'main/profile.html', {"user": user, "cart_items_count": cart_items_count, "wishlist":wishlist, "wishlist_count":wishlist_count})


def order_history(request):
    pass


def oferta(request):
    return render(request, 'main/oferta.html')


def contacts(request):
    return render(request, 'main/contacts.html')


def create_product(request):
    if request.method == "POST":
        new_product_id = 0
        title = request.POST.get("title")
        price = request.POST.get("price")
        image_url = request.POST.get("image_url")

        last_product = Product.objects.all(
        ).order_by('-product_id').first()

        if last_product:
            new_product_id = last_product.product_id + 1
        else:
            new_product_id = 1

        Product.objects.create(
            title=title,
            price=price,
            image_url=image_url,
            product_id=new_product_id
        )
        return redirect('home')

    return render(request, "main/create_product.html")