from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from .models import Category, Auction, Bid, Rating
from .serializers import CategoryListCreateSerializer, CategoryDetailSerializer, AuctionListCreateSerializer, AuctionDetailSerializer, BidListCreateSerializer, BidDetailSerializer, RatingListCreateSerializer, RatingDetailSerializer
from django.db.models import Q
from rest_framework.views import APIView 
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from .permissions import IsOwnerOrAdmin, IsRegisteredUserOrAdmin

# Create your views here.
# class CategoryListCreate(generics.ListCreateAPIView): SI NO NO PUEDO PONER EN LA WEB LAS CATEGORÍAS COMO NOMBRE PARA LOS USUARIOS
#     permission_classes = [IsAdminUser] 
#     queryset = Category.objects.all() 
#     serializer_class = CategoryListCreateSerializer 

class CategoryList(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategoryListCreateSerializer

class CategoryCreate(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategoryListCreateSerializer

class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView): 
    permission_classes = [IsAdminUser] 
    queryset = Category.objects.all() 
    serializer_class = CategoryDetailSerializer 


class AuctionListCreate(generics.ListCreateAPIView):
    permission_classes = [IsRegisteredUserOrAdmin] 
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
        if max_price and min_price and min_price >= max_price:
            raise ValidationError(
                {"precioMax": "PrecioMax must be greater than precioMin."},
                code=status.HTTP_400_BAD_REQUEST
            )
        
        return queryset

class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView): 
    permission_classes = [IsOwnerOrAdmin] 
    queryset = Auction.objects.all() 
    serializer_class = AuctionDetailSerializer


class BidListCreate(generics.ListCreateAPIView):
    permission_classes = [IsRegisteredUserOrAdmin]
    serializer_class = BidListCreateSerializer

    def get_queryset(self):
        auction_id = self.kwargs["id_auctions"]
        return Bid.objects.filter(auction=auction_id).order_by('-price')
    
    def perform_create(self, serializer):
        auction_id = self.kwargs["id_auctions"]
        serializer.save(auction=Auction.objects.get(id=auction_id))

class BidRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = BidDetailSerializer

    def get_queryset(self):
        auction_id = self.kwargs["id_auctions"]
        bid_id = self.kwargs["pk"]
        return Bid.objects.filter(auction_id=auction_id, id=bid_id)
    

class UserAuctionListView(APIView): 
    permission_classes = [IsAuthenticated] 
    def get(self, request, *args, **kwargs): 
        # Obtener las subastas del usuario autenticado 
        user_auctions = Auction.objects.filter(auctioneer=request.user) 
        serializer = AuctionListCreateSerializer(user_auctions, many=True) 
        return Response(serializer.data) 
    
class UserBidListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user_bids = Bid.objects.filter(bidder=request.user)
        serializer = BidListCreateSerializer(user_bids, many=True)
        return Response(serializer.data)
    
class RatingListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RatingListCreateSerializer

    def create(self, request, *args, **kwargs):
        reviewer = request.user
        auction_id = request.data.get("auction")

        if not auction_id:
            return Response({
                "auction": "Auction field is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            existing = Rating.objects.get(reviewer=reviewer, auction_id=auction_id)
            serializer = self.get_serializer(existing, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=200)
        except Rating.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=201)
        
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

class RatingRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = RatingDetailSerializer
    
    def get_queryset(self):
        auction_id = self.kwargs["auction_id"]
        return Rating.objects.filter(reviewer=self.request.user, auction_id=auction_id)