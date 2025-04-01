from drf_spectacular.utils import extend_schema_field 
from rest_framework import serializers 
from django.utils import timezone 
from .models import Category, Auction, Bid

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
    
class BidListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True) 
    class Meta:
        model = Bid
        fields = '__all__'

class BidDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True) 
    class Meta:
        model = Bid
        fields = '__all__'