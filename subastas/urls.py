from django.urls import path
from .views import CategoryList, CategoryCreate, CategoryRetrieveUpdateDestroy, AuctionListCreate, AuctionRetrieveUpdateDestroy, BidListCreate, BidRetrieveUpdateDestroy, UserAuctionListView, UserBidListView, RatingList, RatingRetrieveUpdateDestroy

app_name="auctions"
urlpatterns = [
    path('categorias/', CategoryList.as_view(), name='category-list'),
    path('categorias/crear', CategoryCreate.as_view(), name='category-create'),
    path('categorias/<int:pk>/', CategoryRetrieveUpdateDestroy.as_view(), name='category-detail'),

    path('', AuctionListCreate.as_view(), name='auction-list-create'),
    path('<int:pk>/', AuctionRetrieveUpdateDestroy.as_view(), name='auction-detail'),
    
    path('<int:id_auctions>/pujas/', BidListCreate.as_view(), name='bid-list-create'),
    path('<int:id_auctions>/pujas/<int:pk>/', BidRetrieveUpdateDestroy.as_view(), name='bid-detail'),

    path('mis-subastas/', UserAuctionListView.as_view(), name='action-from-users'), 
    path('mis-pujas/', UserBidListView.as_view(), name='bids-from-users'),

    path('mis-ratings/', RatingList.as_view(), name='rating-list-create'),
    path('mis-ratings/<int:pk>/', RatingRetrieveUpdateDestroy.as_view(), name='rating-detail'),
]