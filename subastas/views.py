from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from .models import Category, Auction, Bid
from .serializers import CategoryListCreateSerializer, CategoryDetailSerializer, AuctionListCreateSerializer, AuctionDetailSerializer, BidListCreateSerializer, BidDetailSerializer
from django.db.models import Q

# Create your views here.
class CategoryListCreate(generics.ListCreateAPIView): 
    queryset = Category.objects.all() 
    serializer_class = CategoryListCreateSerializer 

class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView): 
    queryset = Category.objects.all() 
    serializer_class = CategoryDetailSerializer 

class AuctionListCreate(generics.ListCreateAPIView):
    serializer_class = AuctionListCreateSerializer

    def get_queryset(self):
        queryset = Auction.objects.all()
        params = self.request.query_params
        text = params.get("text", None)
        category = params.get("categoria", None)
        min_price = params.get("precioMin", None)
        max_price = params.get("precioMax", None)
        if text and len(text) < 3:
            raise ValidationError(
                {"texto": "Texto query must be at least 3 characters long."},
                code=status.HTTP_400_BAD_REQUEST
            )
        if text:
            queryset = queryset.filter(
                Q(title__icontains=text) | 
                Q(description__icontains=text)
            )
        if category:
            try:
                category_obj = Category.objects.get(name=category)
                queryset = queryset.filter(category=category_obj)
            except Category.DoesNotExist:
                raise ValidationError(
                    {"categoria": "Categoria does not exist in the database."},
                    code=status.HTTP_404_NOT_FOUND
                )
        if min_price:
            if int(min_price) < 0:
                raise ValidationError(
                    {"precioMin": "PrecioMin must be positive, greater or equal than 0."},
                    code=status.HTTP_400_BAD_REQUEST
                )
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            if int(max_price) < 0:
                raise ValidationError(
                    {"precioMax": "PrecioMax must be positive, greater or equal than 0."},
                    code=status.HTTP_400_BAD_REQUEST
                )
            queryset = queryset.filter(price__lte=max_price)
        return queryset

class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView): 
    queryset = Auction.objects.all() 
    serializer_class = AuctionDetailSerializer

class BidListCreate(generics.ListCreateAPIView):
    serializer_class = BidListCreateSerializer

    def get_queryset(self):
        auction_id = self.kwargs["id_auctions"]
        return Bid.objects.filter(id=auction_id)
    
    def perform_create(self, serializer):
        auction_id = self.kwargs["id_auctions"]
        serializer.save(auction=Auction.objects.get(id=auction_id))

class BidRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BidDetailSerializer

    def get_queryset(self):
        auction_id = self.kwargs["id_auctions"]
        bid_id = self.kwargs["pk"]
        return Bid.objects.filter(auction_id=auction_id, id=bid_id)