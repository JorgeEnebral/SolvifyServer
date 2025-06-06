from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from usuarios.models import CustomUser
from decimal import Decimal

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, blank=False, unique=True)

    class Meta:
        ordering=('id',)
    def __str__(self):
        return self.name
    
    
class Auction(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    closing_date = models.DateTimeField()
    creation_date = models.DateTimeField(auto_now_add=True)
    thumbnail = models.URLField()
    price = models.DecimalField(max_digits=10,
                                decimal_places=2,
                                validators=[MinValueValidator(Decimal('0.00'))])
    stock = models.IntegerField(validators=[MinValueValidator(1)])
    # rating = models.DecimalField(max_digits=3,
    #                              decimal_places=2,
    #                              validators=[MinValueValidator(Decimal('1.00')), MaxValueValidator(Decimal('5.00'))])
    category = models.ForeignKey(Category, related_name='auctions',
        on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    auctioneer = models.ForeignKey(CustomUser, related_name='auctions',
        on_delete=models.CASCADE, default=1)

    class Meta:
        ordering=('id',)
    def __str__(self):
        return self.title
    

class Bid(models.Model):
    auction = models.ForeignKey(Auction, related_name='bids', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    creation_date = models.DateTimeField(auto_now_add=True)
    bidder = models.CharField(max_length=100)

    class Meta:  
        ordering=('id',)  
 
    def __str__(self): 
        return self.bidder


class Rating(models.Model):
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    reviewer = models.ForeignKey(CustomUser, related_name='ratings', on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, related_name='ratings', on_delete=models.CASCADE)

    class Meta:
        ordering=('id',)
        constraints=[
            models.UniqueConstraint(fields=['reviewer', 'auction'], name='unique_reviewer_auction')
        ]

    def __str__(self):
        return f"Auction: {self.auction} - Reviewer: {self.reviewer} - Rating: {self.rating}"


class Comment(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(CustomUser, related_name='comments', on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, related_name='comments', on_delete=models.CASCADE)

    class Meta:
        ordering=('id',)

    def __str__(self):
        return f"Auction: {self.auction} - Author: {self.author} - Title: {self.title}"