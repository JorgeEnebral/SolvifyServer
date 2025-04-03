from drf_spectacular.utils import extend_schema_field 
from rest_framework import serializers 
from django.utils import timezone 
from .models import Category, Auction, Bid
from datetime import timedelta

class CategoryListCreateSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Category 
        fields = ['id','name']  # Indicas qué campos quieres

class CategoryDetailSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Category 
        fields = '__all__'

class AuctionListCreateSerializer(serializers.ModelSerializer): 
    # Estos dos campos los podemos usar así porque existían en el modelo
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)  # read_only=True para que no se pueda modifiar la fecha. Si no lo pongo, aparece creation_date para modificarla y no queremos eso.
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ") 
    # El isOpen no es del modelo, por lo que tenemos que crearlo como un serializador
    isOpen = serializers.SerializerMethodField(read_only=True) 

    class Meta: 
        model = Auction 
        fields = '__all__' 

    @extend_schema_field(serializers.BooleanField())
    def get_isOpen(self, obj): 
        return obj.closing_date > timezone.now()
    
    def validate_closing_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Closing date must be greater than now.")
        elif value < timezone.now() + timedelta(days=15):
            raise serializers.ValidationError("Closing date must be at least 15 days \
                                              greater than creation date.")
        return value
    
class AuctionDetailSerializer(serializers.ModelSerializer): 
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True) 
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    isOpen = serializers.SerializerMethodField(read_only=True)

    class Meta: 
        model = Auction 
        fields = '__all__' 

    @extend_schema_field(serializers.BooleanField())
    def get_isOpen(self, obj): 
        return obj.closing_date > timezone.now()
    
    def validate_closing_date(self, value):
        creation_date = self.instance.creation_date
        if value <= timezone.now():
            raise serializers.ValidationError("Closing date must be greater than now.")
        elif value < creation_date + timedelta(days=15):
            raise serializers.ValidationError("Closing date must be at least 15 days \
                                              greater than creation date.")
        return value
    
class BidListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True) 
    class Meta:
        model = Bid
        fields = '__all__'

    def validate_price(self, value):
        auction = self.initial_data.get("auction")
        if auction:
            last_winning_bid = Bid.objects.filter(auction=auction).order_by("-price").first() # sort descending
            if last_winning_bid and value <= last_winning_bid.price:
                raise serializers.ValidationError(
                    f"The new bid price must be higher than the previous winning bid ({last_winning_bid.price})."
                )
        return value
    
    def validate_auction(self, value):
        auction_serializer = AuctionListCreateSerializer(value)
        if not auction_serializer.data["isOpen"]:
            raise serializers.ValidationError("The auction has already closed. No more bids are allowed.")
        return value

class BidDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True) 
    class Meta:
        model = Bid
        fields = '__all__'

    def validate_price(self, value):
        auction = self.instance.auction if self.instance else None
        if auction:
            last_winning_bid = Bid.objects.filter(auction=auction).orderBy("-price").first() # sort descending
            if last_winning_bid and value <= last_winning_bid.price:
                raise serializers.ValidationError(
                    "The new bid price must be higher than the previous winning bid."
                )
        return value
    
    def validate_auction(self, value):
        auction_serializer = AuctionListCreateSerializer(value)
        if not auction_serializer.data["isOpen"]:
            raise serializers.ValidationError("The auction has already closed. No more bids are allowed.")
        return value