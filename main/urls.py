from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='login'),
    path('register', views.register, name='register'),
    path('home', views.home, name='home')
]
