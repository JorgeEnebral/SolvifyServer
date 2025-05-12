from django.urls import path
from .views import CategoryList, CategoryCreate, CategoryRetrieveUpdateDestroy, AuctionListCreate, AuctionRetrieveUpdateDestroy, BidListCreate, BidRetrieveUpdateDestroy, UserAuctionListView, UserBidListView, RatingList, RatingRetrieveUpdateDestroy, CommentListCreateView, CommentRetrieveUpdateDestroyView, UserCommentListView

app_name="auctions"
urlpatterns = [
    path('categorias/', CategoryList.as_view(), name='category-list'),
    path('categorias/crear', CategoryCreate.as_view(), name='category-create'),
    path('categorias/<int:id_category>/', CategoryRetrieveUpdateDestroy.as_view(), name='category-detail'),

    path('', AuctionListCreate.as_view(), name='auction-list-create'),
    path('<int:id_auctions>/', AuctionRetrieveUpdateDestroy.as_view(), name='auction-detail'),
    
    path('<int:id_auctions>/pujas/', BidListCreate.as_view(), name='bid-list-create'),
    path('<int:id_auctions>/pujas/<int:pk>/', BidRetrieveUpdateDestroy.as_view(), name='bid-detail'),

    path('mis-ratings/', RatingList.as_view(), name='rating-list-create'),
    path('mis-ratings/<int:id_auctions>/', RatingRetrieveUpdateDestroy.as_view(), name='rating-detail'),

    path('<int:id_auctions>/comentarios/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('<int:id_auctions>/comentarios/<int:pk>/', CommentRetrieveUpdateDestroyView.as_view(), name='comment-detail'),  

    path('mis-subastas/', UserAuctionListView.as_view(), name='action-from-users'), 
    path('mis-pujas/', UserBidListView.as_view(), name='bids-from-users'),
    path('mis-comentarios/', UserCommentListView.as_view(), name='comments-from-users'),
]