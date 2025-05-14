from drf_spectacular.utils import extend_schema_field 
from rest_framework import serializers 
from django.utils import timezone 
from .models import Category, Auction, Bid, Rating, Comment
from datetime import timedelta
from django.db.models import Avg


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
    average_rating = serializers.SerializerMethodField()

    class Meta: 
        model = Auction 
        fields = '__all__' 

    @extend_schema_field(serializers.BooleanField())
    def get_isOpen(self, obj): 
        return obj.closing_date > timezone.now()
    
    @extend_schema_field(serializers.DecimalField(max_digits=3, decimal_places=2))
    def get_average_rating(self, obj):
        avg = obj.ratings.aggregate(avg=Avg("rating"))["avg"]
        return round(avg, 2) if avg is not None else None
    
    def validate_closing_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Closing date must be greater than now.")
        elif value < timezone.now() + timedelta(days=15):
            raise serializers.ValidationError("Closing date must be at least 15 days \
                                              greater than creation date.")
        return value
    
    def create(self, validated_data):
        request = self.context["request"]
        auction = Auction.objects.create(**validated_data, auctioneer=request.user)
        Rating.objects.create(
            auction=auction,
            reviewer=self.context["request"].user,
            rating=1
        )
        return auction
    
class AuctionDetailSerializer(serializers.ModelSerializer): 
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True) 
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    isOpen = serializers.SerializerMethodField(read_only=True)
    average_rating = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField(required=False)

    class Meta: 
        model = Auction 
        fields = '__all__' 
        read_only_fields = ['auctioneer', 'creation_date']

    @extend_schema_field(serializers.BooleanField())
    def get_isOpen(self, obj): 
        return obj.closing_date > timezone.now()
    
    @extend_schema_field(serializers.DecimalField(max_digits=3, decimal_places=2))
    def get_average_rating(self, obj):
        avg = obj.ratings.aggregate(avg=Avg("rating"))["avg"]
        return round(avg, 2) if avg is not None else None

    @extend_schema_field(serializers.IntegerField())
    def get_user_rating(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            rating = obj.ratings.filter(reviewer=request.user).first()
            if rating:
                return rating.rating
        return None
    
    def validate_closing_date(self, value):
        if self.instance:
            creation_date = self.instance.creation_date
            if value <= timezone.now():
                raise serializers.ValidationError("Closing date must be greater than now.")
            elif value < creation_date + timedelta(days=15):
                raise serializers.ValidationError("Closing date must be at least 15 days greater than creation date.")
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
            last_winning_bid = Bid.objects.filter(auction=auction).order_by("-price").first() # sort descending
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
    

class RatingListCreateSerializer(serializers.ModelSerializer):
    reviewer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False, default=1)

    class Meta:
        model = Rating
        fields = '__all__'

    def validate(self, data):
        if Rating.objects.filter(reviewer=data['reviewer'], auction=data['auction']).exists():
            raise serializers.ValidationError("You have already rated this auction.")
        return data
    
class RatingRetrieveSerializer(serializers.ModelSerializer):
    reviewer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ['id', 'reviewer', 'auction', 'average_rating']

    @extend_schema_field(serializers.DecimalField(max_digits=3, decimal_places=2))
    def get_average_rating(self, obj):
        avg = Rating.objects.filter(auction=obj.auction).aggregate(avg=Avg("rating"))["avg"]
        return round(avg, 2) if avg is not None else None
    
class RatingUpdateDestroySerializer(serializers.ModelSerializer):
    reviewer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ['id', 'reviewer', 'auction', 'average_rating']

    def validate_rating(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("The provided rating is not an integer between 1 and 5.")
        
        if value < 1 or value > 5:
            raise serializers.ValidationError("The provided rating is not between 1 and 5.")
        
        return value
    
    def validate(self, data):
        request = self.context.get("request")
        instance = getattr(self, 'instance', None)

        reviewer = data.get('reviewer', getattr(instance, 'reviewer', None))
        auction = data.get('auction', getattr(instance, 'auction', None))

        if Rating.objects.filter(reviewer=reviewer, auction=auction).exclude(pk=getattr(instance, 'pk', None)).exists():
            raise serializers.ValidationError("This reviewer has already rated this auction")
        return data


class CommentListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True) 
    update_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True) 

    class Meta:
        model = Comment
        exclude = ['author']
        read_only_fields = ['id', 'auction', 'creation_date', 'update_date']

    def validate_title(self, value):
        if len(value) > 100:
            raise serializers.ValidationError("Title must bu shorter than 100 characters")
        return value
    
    def validate_auction(self, value):
        auction_serializer = AuctionListCreateSerializer(value)
        if not auction_serializer.data["isOpen"]:
            raise serializers.ValidationError("The auction has already closed. No more bids are allowed.")
        return value

class CommentDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True) 
    update_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True) 

    class Meta:
        model = Comment
        exclude = ['author']
        read_only_fields = ['id', 'auction', 'creation_date', 'update_date']

    def validate_title(self, value):
        if len(value) > 100:
            raise serializers.ValidationError("Title must bu shorter than 100 characters")
        return value
    
    def validate_auction(self, value):
        auction_serializer = AuctionListCreateSerializer(value)
        if not auction_serializer.data["isOpen"]:
            raise serializers.ValidationError("The auction has already closed. No more bids are allowed.")
        return value
