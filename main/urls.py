from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('home/cart/', views.cart, name='cart'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('exit/', views.exit, name='exit'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path("about/", views.about, name='about'),
    path("profile/", views.profile, name='profile'),
    path('login/',
         auth_views.LoginView.as_view(
             template_name='main/index.html',  # твой существующий шаблон
             redirect_authenticated_user=True  # если уже вошел - на главную
         ),
         name='login'),

    # 👇 Стандартный логаут
    path('logout/',
         views.exit,  # или можно свой
         name='logout'),
    path("order_history/", views.profile, name='order_history'),
    path('oferta/', views.oferta, name='oferta'),
    path('contacts/', views.contacts, name='contacts'),
]
