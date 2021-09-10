from django.db import models
from django.contrib.auth.models import AbstractUser

"""
    superuser:
        Username: DhairyaSoni
        email: dsdrago27@gmail.com
        Password: Dh@irya2811
"""


# Create your models here.
class User(AbstractUser):
    pass


class Category(models.Model):
    """ this module will store item category. """
    Item_Category = models.TextField()

    def __str__(self):
        return f"{self.pk}. - {self.Item_Category}"


class BuyerOrSeller(models.Model):
    """ this module will store if the user is buyer or seller """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buyer_or_seller")
    buyer = models.BooleanField(default=False)
    seller = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} has roll of buyer -> {self.buyer} seller -> {self.seller}"


class SellItemList(models.Model):
    """ this module will store item details """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="item_to_sell")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="product")
    buyers = models.ManyToManyField(User)
    quantity = models.IntegerField()
    title = models.TextField()
    image_url = models.URLField()
    description = models.TextField()
    price = models.FloatField(default=0.00)

    def __str__(self):
        return f"""
            Title: {self.title}\n
            Description: {self.description}\n
            Price: ${self.price}\n
            Image URL: {self.image_url}\n
            Quantity: {self.quantity}\n
            Category: {self.category}\n\n\n 
        """


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="i_want_this")
    item = models.ManyToManyField(SellItemList)

    def __str__(self):
        return f"""
            {self.user.username}\n
                \t{self.item}\n\n
        """


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment")
    item = models.ForeignKey(SellItemList, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()

    def __str__(self):
        return f"""
            User: {self.user.username}\n
            Item: {self.item.title}\n
            Comment: {self.comment}\n\n\n
        """
