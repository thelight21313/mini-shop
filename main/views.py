from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from .models import Account, Product, Cart, Wishlist, Order, Category
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import date
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django import forms
from django.contrib.auth.decorators import login_required
import uuid
from yookassa import Configuration, Payment
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import CounterSerializer, ProductserForUpdatePage
from rest_framework.views import APIView
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Создаем пользователя
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'main/register.html', {'form': form})


class homeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = ''
        action = request.data.get('action')
        username = request.user.username
        is_favorite = False
        if action == "add_to_cart":
            _id = request.data.get('product_id')
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
                message = 'Товар добавлен в корзину'
            else:
                cart_item = Cart.objects.get(product_id=_id, user=username)
                cart_item.count += 1
                cart_item.save()
                message = 'количество товара в корзине увеличено'

        elif action == "add_to_favorites":
            _id = request.data.get('product_id')
            info = Product.objects.get(product_id=int(_id))
            wish = Wishlist.objects.filter(product_id=_id, username=username)
            if not wish.exists():
                new_wish= Wishlist.objects.create(
                    title=info.title,
                    price=info.price,
                    image_url=info.image_url,
                    product_id=info.product_id,
                    username=username
                )
                message = 'товар добавлен в избранное'
                is_favorite = True
            elif wish.exists():
                wish.delete()
                message = 'товар удалён из избранного'
                is_favorite = False
        elif action == "change_category":
            category = request.data.get('category_name')
            if category == "all":
                products = Product.objects.all()
            else:
                products = Product.objects.filter(Q(category__name=category, category__parent=category))
            wishlist_ids = list(
                Wishlist.objects.filter(username=username).values_list('product_id', flat=True)
            )
            serializer = ProductserForUpdatePage(
                products,
                many=True,
                context={"wishlist_ids": wishlist_ids}
            )
            cart_count = Cart.objects.filter
            return Response({
                'message': f'Выбрана категория: {category}',
                'cart_count': cart_count,
                'products': serializer.data,
                'wishlist_product_ids': wishlist_ids
            })

        cart_count = Cart.objects.filter(user=username).count()
        return Response({
            'message': message,
            'is_favorite': is_favorite,
            'cart_count': cart_count
        })


@login_required
def home(request):
    message = ''
    username = request.user.username
    cart_count = Cart.objects.filter(user=username).count()
    products = Product.objects.all()
    is_seller = request.user.groups.filter(name='seller').exists()
    payment_success = request.GET.get('payment_success') == 'true'
    order_id = request.GET.get('order_id')

    # Если нужно, очищаем корзину после успешной оплаты
    if payment_success and order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user.username)
            if order.status == 'completed':
                # Очищаем корзину
                Cart.objects.filter(user=request.user.username).delete()
        except Order.DoesNotExist:
            pass
    cart_count = Cart.objects.filter(user=username).count()
    message = ''
    context = {
        "message": '',
        'cart_count': cart_count,
        "products": products,
        "is_seller": is_seller,
        "show_payment_success": payment_success,  # Флаг для JS
        "order_id": order_id if payment_success else None,
    }
    return render(request, "main/home.html", context)


class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        username = request.user.username
        product_id = request.data.get('product_id')
        action = request.data.get('action')

        cart_item = Cart.objects.get(product_id=product_id, user=username)

        if action == 'plus':
            cart_item.count += 1
            cart_item.save()
        elif action == 'minus':
            if cart_item.count > 1:
                cart_item.count -= 1
                cart_item.save()
            else:
                cart_item.delete()
        elif action == 'remove':
            cart_item.delete()
        cart_items = Cart.objects.filter(user=username)
        for item in cart_items:
            item.total_price = item.price * item.count
        cart_total = sum([item.total_price for item in cart_items])
        if cart_item.pk:
            serilizator = CounterSerializer(cart_item)
            response_data = serilizator.data
        else:
            response_data = {'product_id': product_id, 'count': 0}
        response_data['cart_total'] = cart_total
        response_data['items_count'] = cart_items.count()
        cart_count = Cart.objects.filter(user=username).count()
        response_data['cart_count'] = cart_count
        return Response(response_data, status=status.HTTP_200_OK)


@login_required
def cart(request):
    username = request.user.username
    cart_items = Cart.objects.filter(user=username)
    for item in cart_items:
        item.total_price = item.price * item.count
    cart_total = sum([item.total_price for item in cart_items])
    cart_count = Cart.objects.filter(user=username).count()
    context = {
        "cart_count": cart_count,
        "cart_items": cart_items,
        "cart_total": cart_total
    }
    return render(request, "main/cart.html", context)


@login_required
def create_payment(request):
    if request.method != "POST":
        return redirect('cart')
    Configuration.account_id = "1231470"
    Configuration.secret_key = "test_IUe2Mi_ainNSY1reHVY9Gk6d9gTqGIKKUkEt2Ni8A7U"

    username = request.user.username
    cart_items = Cart.objects.filter(user=username)
    cart_total = sum(item.price * item.count for item in cart_items)

    order = Order.objects.create(
        user=username,
        total_amount=cart_total,
        status='pending',
        payment_id=None,  # заполним после создания платежа
        items=json.dumps([{
            'title': item.title,
            'price': item.price,
            'count': item.count,
            'product_id': item.product_id
        } for item in cart_items])
    )

    idempotence_key = str(uuid.uuid4())
    try:
        return_url = request.build_absolute_uri(
            f"{reverse('home')}?payment_success=true&order_id={order.id}"
        )

        payment = Payment.create({
            "amount": {
                "value": str(cart_total),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url  # Полный URL с доменом
            },
            "capture": True,
            "description": f"Оплата заказа #{order.id} пользователя {username}",
            "metadata": {
                "order_id": order.id,
                "user": username
            }
        }, idempotence_key)
        order.payment_id = payment.id
        order.save()
        return redirect(payment.confirmation.confirmation_url)

    except Exception as e:
        order.status = "failed"
        order.save()
        print(f"Ошибка создания платежа: {e}")
        return redirect('cart')


@csrf_exempt
def yookassa_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=400)

    try:
        event_json = json.loads(request.body.decode('utf-8'))
        event = event_json.get('event')
        payment_data = event_json.get('object', {})
        payment_id = payment_data.get('id')

        try:
            order = Order.objects.get(payment_id=payment_id)
        except Order.DoesNotExist:
            return HttpResponse(status=400)

        if event == "payment.succeeded":
            order.status = "completed"
            order.save()
            deleted_count = Cart.objects.filter(user=order.user).delete()
        elif event == "payment.canceled":
            order.status = "canceled"
            order.save()

        elif event == "payment.waiting_for_capture":
            order.status = 'pending_capture'
            order.save()

        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=500)


def exit(request):
    logout(request)
    return redirect('login')


@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    is_in_wishlist = False

    if request.user.is_authenticated:
        if Wishlist.objects.filter(username=request.user.username, product_id=product_id).exists():
            is_in_wishlist = True
    context = {
        'product': product,
        'is_in_wishlist': is_in_wishlist
    }
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
    wishlist = Wishlist.objects.filter(username=username)
    for wish in wishlist:
        wishlist_count+=1
    orders = Order.objects.filter(user=username).order_by('-created_at')
    cart_count = Cart.objects.filter(user=username).count()
    total_spent = sum(order.total_amount for order in orders.filter(status='completed'))
    context = {"user": request.user,
               "cart_items_count": cart_items_count,
               "wishlist": wishlist,
               "wishlist_count":  wishlist_count,
               "orders": orders,
               "total_spent": total_spent,
               "cart_count": cart_count}
    return render(request, 'main/profile.html', context)


@login_required
def order_history(request):
    pass


@login_required
def oferta(request):
    return render(request, 'main/oferta.html')


@login_required
def contacts(request):
    return render(request, 'main/contacts.html')


@login_required
def create_product(request):
    if request.method == "POST":
        new_product_id = 0
        title = request.POST.get("title")
        price = request.POST.get("price")
        image_url = request.POST.get("image_url")
        description = request.POST.get("description")

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
            product_id=new_product_id,
            description = description
        )
        return redirect('home')

    return render(request, "main/create_product.html")


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user.username).order_by('-created_at')

    return render(request, 'main/order_history.html', {
        'orders': orders,
        'user': request.user,
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user.username)

    return render(request, 'main/order_detail.html', {
        'order': order,
        'user': request.user,
    })