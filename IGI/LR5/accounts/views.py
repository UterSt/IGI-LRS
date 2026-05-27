import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from shop.forms import CustomerProfileForm
from shop.models import Customer

logger = logging.getLogger("accounts")

#register view
def register(request):
    if request.user.is_authenticated:
        return redirect("shop:home")
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        logger.info("New user registered: %s", user.username)
        messages.success(request, f"Добро пожаловать, {user.first_name}!")
        return redirect("shop:cabinet")
    return render(request, "accounts/register.html", {"form": form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("shop:home")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        logger.info("User logged in: %s", user.username)
        next_url = request.GET.get("next", "shop:home")
        return redirect(next_url)
    return render(request, "accounts/login.html", {"form": form})


@login_required
def user_logout(request):
    logger.info("User logged out: %s", request.user.username)
    logout(request)
    return redirect("shop:home")


@login_required
def profile(request):
    customer = getattr(request.user, "customer_profile", None)
    if customer is None:
        customer = Customer(user=request.user, email=request.user.email)

    form = CustomerProfileForm(request.POST or None, instance=customer)
    if form.is_valid():
        c = form.save(commit=False)
        c.user = request.user
        c.save()
        messages.success(request, "Профиль обновлён.")
        return redirect("accounts:profile")

    return render(request, "accounts/profile.html", {"form": form, "customer": customer})
