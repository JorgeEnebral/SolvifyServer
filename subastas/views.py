from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError, NotFound
from .models import Category, Auction, Bid, Rating, Comment
from .serializers import CategoryListCreateSerializer, CategoryDetailSerializer, AuctionListCreateSerializer, AuctionDetailSerializer, BidListCreateSerializer, BidDetailSerializer, RatingListCreateSerializer, RatingRetrieveSerializer, RatingUpdateDestroySerializer, CommentListCreateSerializer, CommentDetailSerializer
from django.db.models import Q
from rest_framework.views import APIView 
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from .permissions import IsOwnerOrAdmin, IsRegisteredUserOrAdmin, IsOwnerOrAdminAuction

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

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsRegisteredUserOrAdmin()]
    
class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView): 
    queryset = Auction.objects.all() 
    serializer_class = AuctionDetailSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsOwnerOrAdminAuction()]


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
        return Bid.objects.filter(auction=auction_id, id=bid_id)
    

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
    
class UserCommentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_comments = Comment.objects.filter(author=request.user)
        serializer = CommentListCreateSerializer(user_comments, many=True)
        return Response(serializer.data)
    

class RatingList(generics.ListCreateAPIView):
    serializer_class = RatingListCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(reviewer=self.request.user)
    
    def perform_create(self, serializer):
        auction_id = self.request.data.get("auction")
        if Rating.objects.filter(reviewer=self.request.user, auction=auction_id).exists():
            raise ValidationError("Ya has calificado este producto.")
        serializer.save(reviewer=self.request.user)
    
class RatingRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        auction_id = self.kwargs.get("id_auctions")
        user = self.request.user

        try:
            return Rating.objects.get(auction_id=auction_id, reviewer=user)
        except Rating.DoesNotExist:
            raise NotFound("There is no rating for this auction made by this user.")
        
    def get_serializer_class(self):
        if self.request.method == "GET":
            return RatingRetrieveSerializer
        return RatingUpdateDestroySerializer
    

class CommentListView(generics.ListCreateAPIView):
    serializer_class = CommentListCreateSerializer
    permission_classes = [AllowAny]
    queryset = Comment.objects.all()

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentListCreateSerializer

    def get_queryset(self):
        auction_id = self.kwargs['id_auctions']
        return Comment.objects.filter(auction_id=auction_id)

    def perform_create(self, serializer):
        auction_id = self.kwargs['id_auctions']
        serializer.save(author=self.request.user, auction_id=auction_id)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentDetailSerializer
    queryset = Comment.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsOwnerOrAdmin()]
