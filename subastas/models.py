from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from usuarios.models import CustomUser

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
                                validators=[MinValueValidator(0)])
    stock = models.IntegerField(validators=[MinValueValidator(1)])
    rating = models.DecimalField(max_digits=3,
                                 decimal_places=2,
                                 validators=[MinValueValidator(1), MaxValueValidator(5)])
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
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    creation_date = models.DateTimeField(auto_now_add=True)
    bidder = models.CharField(max_length=100)

    class Meta:  
        ordering=('id',)  
 
    def __str__(self): 
        return self.bidder
