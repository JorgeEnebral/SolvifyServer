from django.shortcuts import render
from rest_framework import generics 
from .models import Category, Auction, Bid
from .serializers import CategoryListCreateSerializer, CategoryDetailSerializer, AuctionListCreateSerializer, AuctionDetailSerializer, BidListCreateSerializer, BidDetailSerializer

# Create your views here.
class CategoryListCreate(generics.ListCreateAPIView): 
    queryset = Category.objects.all() 
    serializer_class = CategoryListCreateSerializer 

class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView): 
    queryset = Category.objects.all() 
    serializer_class = CategoryDetailSerializer 

class AuctionListCreate(generics.ListCreateAPIView): 
    queryset = Auction.objects.all() 
    serializer_class = AuctionListCreateSerializer 

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