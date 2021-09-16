from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db import IntegrityError
from .models import User, Category, Comment, Cart
from .models import SellItemList as SI
from .models import BuyerOrSeller as BOS


# Create your views here.
def index(req):
    if req.user.is_authenticated:
        arr = check_roll(req.user)
        return render(req, "index/index.html", arr)
    else:
        return render(req, 'index/index.html')


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "index/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        buyer = request.POST.get("buyer")
        seller = request.POST.get("seller")
        if buyer != None or seller != None:
            if password != confirmation:
                return render(request, "index/register.html", {
                    "message": "Passwords must match."
                })

            # Attempt to create new user
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                b = False
                s = False
                if buyer is not None and seller is not None:
                    b = True
                    s = True
                elif buyer is not None and seller is None:
                    b = True
                    s = False
                elif buyer is None and seller is not None:
                    b = False
                    s = True
                bos = BOS(user=user, buyer=b, seller=s)
                bos.save()
            except IntegrityError:
                return render(request, "index/register.html", {
                    "message": "Username already taken."
                })
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "index/register.html", {
                "message": "Select your roll as a seller or as a buyer."
            })
    else:
        return render(request, "index/register.html")


def check_roll(user):
    bos = BOS.objects.get(user=user)
    buyer = bos.buyer
    seller = bos.seller
    print(buyer, " --- ", seller)
    return {"buyer": buyer, "seller": seller}
