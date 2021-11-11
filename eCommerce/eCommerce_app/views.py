from django.core import serializers
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse
from django.db import IntegrityError
from .models import User, Category, Comment, Cart
from .models import SellItemList as SI


# Create your views here.
def index(request):
    items = SI.objects.all()
    if request.user.is_authenticated:
        return render(request, "index/display.html", {"items" : items, "title": "Index", "authenticate": True})
    else:
        return render(request, 'index/display.html', {"items" : items, "title": "Index", "authenticate": False})


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
            return render(request, "index/login.html", {
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
        if password != confirmation:
            return render(request, "index/register.html", {
                "message": "Passwords must match."
            })
            # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "index/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "index/register.html")


def new_item(request):
    categories = Category.objects.all()
    categories_name = []
    for category in categories:
        categories_name.append(category.Item_Category)
    if (str (request.method)) == "POST":
        title = request.POST["item_title"]
        description = request.POST["item_description"]
        price = request.POST["item_price"]
        url = request.POST["item_image_url"]
        quantity = request.POST.get("quantity")
        category = request.POST["item_category"]
        cat = Category.objects.get(Item_Category = category)
        user = request.user
        add_item = SI(category = cat, seller= user, quantity=quantity, title =title, image_url = url,
                      description = description, price = price)
        add_item.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "index/newitem.html", {"categories_name": categories_name})


def details(request, item_id):
    try:
        item_details = SI.objects.get(id=item_id)
    except SI.DoesNotExist:
        print("Err")
    return render(request, "index/details.html", {"info": item_details})


def add_comment(request):
    if request.method == "POST":
        comment_text = request.POST.get("comment")
        item_id = request.POST.get("item_id")
        username = request.POST.get("username")
        user = User.objects.get(username = username)
        item = SI.objects.get(id = item_id)
        comment = Comment(user = user, item = item, comment = comment_text)
        comment.save()
        return HttpResponse()
    else:
        raise Http404("There is no page like this.")


def get_comments(request, item_id):
    item = SI.objects.get(id = item_id)
    comments = Comment.objects.all().filter(item = item)
    comments = serializers.serialize("json", comments)
    return JsonResponse({"comments": comments})
