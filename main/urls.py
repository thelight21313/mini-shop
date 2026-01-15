from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CartAPIView, homeAPIView
from django_ratelimit.decorators import ratelimit

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('api/', homeAPIView.as_view(), name='main_api'),
    path('orders/', views.order_history, name='order_history'),
    path('order_history/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('home/cart/', views.cart, name='cart'),
    path('api/cart/', views.CartAPIView.as_view(), name='cart_api'),
    path('exit/', views.exit, name='exit'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path("about/", views.about, name='about'),
    path("profile/", views.profile, name='profile'),
    path('login/',
         ratelimit(key='ip', rate='3/m', method='POST', block=True)(
             auth_views.LoginView.as_view(
                 template_name='main/index.html',
                 redirect_authenticated_user=True
             )
         ),
         name='login'),
    path('logout/', views.exit, name='logout'),
    path("order_history/", views.profile, name='order_history'),
    path('oferta/', views.oferta, name='oferta'),
    path('contacts/', views.contacts, name='contacts'),
    path('create_payment/', views.create_payment, name='create_payment'),
    path('create_product/', views.create_product, name='create_product'),
    path('yookassa/webhook/', views.yookassa_webhook, name='yookassa_webhook'),
]
