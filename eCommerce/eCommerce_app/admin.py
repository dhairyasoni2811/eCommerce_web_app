from django.contrib import admin
from .models import BuyerOrSeller, Category, Cart, Comment, SellItemList, User

# Register your models here.
admin.site.register(BuyerOrSeller)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Comment)
admin.site.register(SellItemList)
admin.site.register(User)