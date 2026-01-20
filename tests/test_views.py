import pytest, json
import main.views as view
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from main.models import Product, Cart1, Wishlist1, Order1, Category
from unittest.mock import patch
from unittest.mock import patch, MagicMock


@pytest.fixture()
def test_user(db):
    return User.objects.create_user(
        username='test_user',
        password='ComplexPass123'
    )
@pytest.fixture()
def test_category(db):
    return Category.objects.create(
        id=2,
        name="Test Category"
    )

@pytest.fixture()
def test_product(db, test_category):
    return Product.objects.create(
        product_id=1,
        title="test",
        price=100,
        image_url="",
        wishlist=False,
        description="",
        category=test_category
    )


@pytest.fixture()
def authenticated_client(test_user):
    user = test_user
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture()
def test_cart_object(test_product, test_user):
    return Cart.objects.create(
                product_id=test_product.product_id,
                title=test_product.title,
                price=test_product.price,
                image_url=test_product.image_url,
                user=test_user,
                count=2,
                item_total=test_product.price * 2

            )


@pytest.fixture
def test_order(db, test_product, test_user):
    return Order.objects.create(
            user=test_user,
            total_amount=200,
            status='completes',
            payment_id='test_payment_123',
            items=json.dumps([{
                'title': test_product.title,
                'price': test_product.price,
                'count': 2,
                'product_id': test_product.product_id
            }])
        )


class TestRegistration():
    def test_register_creates_new_user(self, db):
        client = Client()
        response = client.post('/register/', {"username": "test_user", "password1": "12345ASsddf", "password2": "12345ASsddf"}, secure=True)
        assert response.status_code == 302
        assert response.url == reverse('login')
        assert User.objects.filter(username="test_user").exists()
        assert User.objects.filter(username="test_user").count() == 1


class TestHomeApi():
    def test_HomeApi_add_to_cart(self, test_user, test_product, authenticated_client):
        data = {
            'action': "add_to_cart",
            'product_id': test_product.product_id
        }

        assert Cart.objects.count() == 0
        client = authenticated_client
        response = client.post(reverse('main_api'), data, content_type='application/json', secure=True)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data['message'] == 'Товар добавлен в корзину'
        assert Cart.objects.count() == 1
        response = client.post(reverse('main_api'), data, content_type='application/json', secure=True)
        response_data = response.json()
        assert response_data['message'] == 'количество товара в корзине увеличено'

    def test_HomeApi_add_to_wishlist(self, test_user, test_product, authenticated_client):
        data = {
            'action': "add_to_favorites",
            'product_id': test_product.product_id
        }
        assert Wishlist.objects.count() == 0
        client = authenticated_client
        response = client.post(reverse('main_api'), data, content_type='application/json', secure=True)
        assert Wishlist.objects.count() == 1
        response_data = response.json()
        assert response_data['message'] == 'товар добавлен в избранное'
        assert response_data['is_favorite'] is True
        response = client.post(reverse('main_api'), data, content_type='application/json', secure=True)
        response_data = response.json()
        assert response_data['message'] == 'товар удалён из избранного'
        assert response_data['is_favorite'] is False


class Test_home_view():
    def test_delete_cart(self, test_user, test_product, test_cart_object, test_order, authenticated_client):
        assert Cart.objects.filter(user=test_user).count() == 1
        client = authenticated_client
        test_order.status = 'completed'
        test_order.save()
        response = client.get(
            '/',
            {'payment_success': 'true', 'order_id': test_order.id},
            secure=True
        )
        assert Cart.objects.filter(user=test_user).count() == 0

    def test_not_delete_with_wrong_status_code(self, test_user, test_product, test_cart_object, test_order, authenticated_client):
        assert Cart.objects.filter(user=test_user).count() == 1
        client = authenticated_client
        test_order.status = 'pending'
        test_order.save()
        response = client.get(
            '/',
            {'payment_success': 'true', 'order_id': test_order.id},
            secure=True
        )
        assert Cart.objects.filter(user=test_user).count() == 1

    def test_wrong_order_id(self, test_user, test_product, test_cart_object, test_order, authenticated_client):
        assert Cart.objects.filter(user=test_user).count() == 1
        client = authenticated_client
        test_order.status = 'completed'
        test_order.save()
        response = client.get(
            '/',
            {'payment_success': 'true', 'order_id': -9999999},
            secure=True
        )
        assert Cart.objects.filter(user=test_user).count() == 1
        assert response.status_code == 200


class Test_CartAPI():
    def test_actions(self, test_user, test_product, test_cart_object, test_order, authenticated_client):
        assert Cart.objects.filter(user=test_user).count() == 1
        data = {
            'action': 'plus',
            'product_id': test_product.product_id,

        }
        client = authenticated_client
        response = client.post(reverse('cart_api'), data, secure=True)
        cart_item = Cart.objects.get(user=test_user, product_id=test_product.product_id)

        assert Cart.objects.filter(user=test_user, product_id=test_product.product_id).exists()
        assert cart_item.count == 3
        assert response.status_code == 200
        data['action'] = 'minus'
        response = client.post(reverse('cart_api'), data, secure=True)
        cart_item.refresh_from_db()
        assert cart_item.count == 2
        response_data = response.json()
        assert response_data['cart_total'] == test_product.price * 2
        assert response.status_code == 200
        data['action'] = 'remove'
        response = client.post(reverse('cart_api'), data, secure=True)
        assert not Cart.objects.filter(user=test_user, product_id=test_product.product_id).exists()
        assert response.status_code == 200


@pytest.mark.django_db
class Test_paymnet_system():
    @patch('yookassa.Payment.create')
    def test_create_payment_success(self, mock_payment_create, authenticated_client, test_user, test_cart_object):
        mock_payment_create.return_value.id = "test_payment_id"
        mock_payment_create.return_value.confirmation.confirmation_url = "yookassa.ru"

        # Вызываем твой view
        response = authenticated_client.post('/create_payment/', secure=True)

        # Проверки
        assert response.status_code == 302
        assert response.url == "yookassa.ru"

        orders = Order.objects.filter(user=test_user)
        assert orders.count() == 1

        order = orders.first()
        assert order.payment_id == "test_payment_id"
        assert order.status == 'pending'
        assert order.total_amount == 200.00

        mock_payment_create.assert_called_once()
        call_args = mock_payment_create.call_args[0][0]
        assert float(call_args['amount']['value']) == 200.0
        assert 'payment_success=true' in call_args['confirmation']['return_url']

    def test_webhook_payment_succeeded(self, client, test_user):
        order = Order.objects.create(
            user=test_user,
            total_amount=200,
            status='pending',
            payment_id='pay_test_succeeded_id'
        )
        Cart.objects.create(user=test_user, title="Товар А", price=100, count=1, product_id=1)
        Cart.objects.create(user=test_user, title="Товар Б", price=100, count=1, product_id=2)

        payload = {
            "event": "payment.succeeded",
            "object": {
                "id": "pay_test_succeeded_id",
                "status": "succeeded"
            }
        }

        response = client.post(
            reverse('yookassa_webhook'),
            data=json.dumps(payload),
            content_type='application/json',
            secure=True
        )

        assert response.status_code == 200  # ЮKassa ожидает ответ 200 OK
        order.refresh_from_db()  # Обновляем объект заказа из БД
        assert order.status == 'completed'

        # Проверяем, что корзина пользователя пуста
        assert Cart.objects.filter(user=test_user).count() == 0


@pytest.mark.django_db
class Test_create_product():
    def test(self, authenticated_client, test_category):
        products = Product.objects.all()
        assert products.count() == 0
        data = {
            'title': "test",
            'price': 200,
            'image_url': 'test_url.com',
            'description': "test description",
            'final_category_id': test_category.id
        }
        client = authenticated_client
        response = client.post(reverse('create_product'), data, secure=True)
        assert response.status_code == 302
        assert products.count() == 1