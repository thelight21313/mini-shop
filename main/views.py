from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .models import Account
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError



def index(request):
    ph = PasswordHasher()

    def login(stored_hash: str, input_password: str) -> bool:
        try:
            ph.verify(stored_hash, input_password)
            return True
        except VerifyMismatchError:
            return False
    error = ''
    if request.method == "POST":
        username_ = request.POST.get("login")
        password = request.POST.get("password")

        try:
            user = Account.objects.get(username=username_)
            password_hash = user.password_hash
            if login(password_hash, password):
                request.session['username'] = username_
                print("ЯЯ")
                return redirect('home')

        except:
            error = "Неправильный логин или пароль"
            context = {"error": error}
            return render(request, 'main/index.html', context)

    context = {"error": error}
    return render(request, 'main/index.html', context)


def register(request):
    error = ""
    if request.method == "POST":
        username_ = request.POST.get("name")
        password1 = request.POST.get("p1")
        password2 = request.POST.get("p2")
        if Account.objects.filter(username=username_).exists():
            error = "username занят"
        else:
            if password1 == password2:
                hash = PasswordHasher().hash(password1)
                Account.objects.create(username= username_, password_hash=hash)
                return redirect('login')
            else:
                error = "Пароли не совпадают"
    context = {"error": error}
    return render(request, 'main/register.html', context)


def home(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')
    return render(request, 'main/home.html', {"username": username})
