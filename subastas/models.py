from django.db import models

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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    category = models.ForeignKey(Category, related_name='auctions',
    on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    
    class Meta:
        ordering=('id',)
    def __str__(self):
        return self.title
