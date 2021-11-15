from django.core import serializers
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse
from django.db import IntegrityError
from .models import User, Category, Comment, Cart
from .models import SellItemList as SI


# Create your views here.
def index(request, filter_name=None):
        if filter_name is not None:
            item = SI.objects.all().filter(title__contains = f"{filter_name}").order_by("-id")
            return render(request, "index/display.html", {"items": [item], "title": "Name Filter"})
        else:
            item = SI.objects.all().order_by("-id")
            return render(request, 'index/display.html', {"items": [item], "title": "Index"})


def filter_category(request, category_name):
    if category_name == "All":
        items = SI.objects.all().order_by("-id")
    else:
        category = Category.objects.get(Item_Category=category_name)
        items = SI.objects.all().filter(category=category).order_by("-id")
    return render(request, 'index/display.html', {"items": [items], "title": "Category Filter"})


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
        print(request.POST.get("update"))
        print(request.POST.get("item_id"))
        title = request.POST["item_title"]
        description = request.POST["item_description"]
        price = request.POST["item_price"]
        url = request.POST["item_image_url"]
        quantity = request.POST.get("quantity")
        category = request.POST["item_category"]
        cat = Category.objects.get(Item_Category=category)
        user = request.user
        if (str (request.POST.get("update"))) != "update" :
            add_item = SI(category=cat, seller=user, quantity=quantity, title=title, image_url=url,
                          description=description, price=price)
            add_item.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            item_id = request.POST.get("item_id")
            item = SI.objects.get(id = item_id)
            item.title = title
            item.description = description
            item.image_url = url
            item.price = price
            item.quantity = quantity
            item.category = cat
            item.save()
            return HttpResponseRedirect(reverse("my_items"))
    else:
        return render(request, "index/newitem.html", {"categories_name": categories_name})


def details(request, item_id):
    try:
        item_details = SI.objects.get(id=item_id)
        user = request.user
        cart_items = Cart.objects.filter(user = user, item = item_details)
        in_cart = ((str(cart_items)) == "<QuerySet []>")
        return render(request, "index/details.html", {"info": item_details, "cart": f"{in_cart}"})
    except SI.DoesNotExist:
        raise Http404("Item does not exist.")


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
    comments = Comment.objects.all().filter(item = item).order_by("-id")
    comments = serializers.serialize("json", comments)
    return JsonResponse({"comments": comments})


def add_to_cart(request):
    if request.method == "POST":
        username = request.POST["username"]
        item_id = request.POST["item_id"]
        user = User.objects.get(username=username)
        item = SI.objects.get(id=item_id)
        adding_item_to_cart = (str(Cart.objects.all().filter(user=user, item=item))) == "<QuerySet []>"
        print(adding_item_to_cart)
        if adding_item_to_cart:
            add_cart = Cart(user=user)
            add_cart.save()
            add_cart.item.add(item)
        return HttpResponseRedirect(reverse("show_cart"))
    else:
        raise Http404("There is no page like this.")


def remove_from_cart(request):
    if request.method == "POST":
        username = request.POST["username"]
        item_id = request.POST["item_id"]
        user = User.objects.get(username=username)
        item = SI.objects.get(id=item_id)
        cart_item = Cart.objects.get(user = user, item = item)
        cart_item.delete()
        return HttpResponseRedirect(reverse("show_cart"))
    else:
        raise Http404("There is no page like this.")


def get_cart(request):
    if request.user.is_authenticated:
        user = request.user
        items = Cart.objects.all().filter(user=user)
        item_q = []
        for item in items:
            item_q.append(item.item.all().order_by("-id"))
        return render(request, "index/display.html", {"items": item_q, "title": "My Cart"})
    else:
        raise Http404("Please sign in to see your cart.")


def buy_item(request, item_id = None):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        item = SI.objects.get(id = item_id)
        quantity = item.quantity
        latest_quantity = quantity - 1
        if latest_quantity>=0:
            SI.objects.filter(id = item_id).update(quantity = latest_quantity)
    item = SI.objects.get(id = item_id)
    quantity = item.quantity
    return JsonResponse({"quantity": quantity})


def my_items(request):
    user = request.user
    items = SI.objects.all().filter(seller = user).order_by("-id")
    return render(request, "index/display.html", {"items": [items], "title": "My Items"})


def item_filter(request):
    if request.method == "POST":
        item_name = request.POST.get("item_name")
        path = request.POST.get("path")
        path = path.split("/")
        print(path)
        if path[1] == "" or path[1] == "filter" or path[1] == "category":
            return HttpResponseRedirect(f"filter/{item_name}")
        elif path[1] == "show_cart":
            return HttpResponseRedirect(f"show_cart/filter/{item_name}")
    else:
        raise Http404("There is no page like this.")


def edit_item(request, item_id):
    item = SI.objects.get(id = item_id)
    categories = Category.objects.all()
    categories_name = []
    for category in categories:
        categories_name.append(category.Item_Category)
    return render(request, "index/newitem.html", {"info": item, "edit":"edit", "categories_name": categories_name})

