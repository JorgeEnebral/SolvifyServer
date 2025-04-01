from django.urls import path
from .views import CategoryListCreate, CategoryRetrieveUpdateDestroy, AuctionListCreate, AuctionRetrieveUpdateDestroy, BidListCreate, BidRetrieveUpdateDestroy 

app_name="auctions"
urlpatterns = [
    path('subastas/categorias', CategoryListCreate.as_view(), name='category-list-create'),
    path('subastas/categorias/<int:pk>/', CategoryRetrieveUpdateDestroy.as_view(), name='category-detail'),
    path('', AuctionListCreate.as_view(), name='auction-list-create'),
    path('<int:pk>/', AuctionRetrieveUpdateDestroy.as_view(), name='auction-detail'),
    path('subastas/<int:id_auctions>/pujas/', BidListCreate.as_view(), name='bid-list-create'),
    path('subastas/<int:id_auctions>/pujas/<int:pk>/', BidRetrieveUpdateDestroy.as_view(), name='bid-detail')
]