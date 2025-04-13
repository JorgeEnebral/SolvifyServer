import os
import sys
import django
import requests
import random
from datetime import datetime

# Configura el directorio base de tu proyecto Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "solvifyServer.settings")
django.setup()

# Ahora puedes importar los modelos
from subastas.models import Category, Auction, Bid  
from usuarios.models import CustomUser
from django.utils import timezone


def fetch_products():
    url = "https://dummyjson.com/products"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json().get("products", [])
    else:
        print("Error al obtener los datos:", response.status_code)
        return []
    
def clear_sqlite_database():
    """Elimina todas las subastas y categorías de la base de datos."""
    Bid.objects.all().delete()
    Auction.objects.all().delete()
    Category.objects.all().delete()
    CustomUser.objects.all().delete()
    print("Base de datos vaciada.")

def crear_usuarios():
    # SUPERUSUARIO
    admin = CustomUser.objects.create_superuser(
            username="solvify_admin",
            first_name="solvify",
            last_name="admin",
            email="solvify_admin@example.com",
            password="solvify_admin_1234",
            is_staff=True,
            is_active=True,
            is_superuser=True,
            last_login=timezone.now(),
            date_joined=timezone.now(),
            birth_date="1990-01-01",
            locality="Centro",
            municipality="Capital"
        )
    
    user1 = CustomUser.objects.create(
        username="user1",
        first_name="user",
        last_name="1",
        email="user1@example.com",
        password="user1_1234",
        is_staff=False,
        is_active=False,
        is_superuser=False,
        last_login=timezone.now(),
        date_joined=timezone.now(),
        birth_date="1990-01-01",
        locality="Centro",
        municipality="Capital"
    )

    user2 = CustomUser.objects.create(
        username="user2",
        first_name="user",
        last_name="2",
        email="user2@example.com",
        password="user2_1234",
        is_staff=False,
        is_active=False,
        is_superuser=False,
        last_login=timezone.now(),
        date_joined=timezone.now(),
        birth_date="1990-01-01",
        locality="Centro",
        municipality="Capital"
    )
    
    return admin, user1, user2
    
def crear_pujas(productos, admin, user1, user2):

    def crear_puja(user, auction, price):
        Bid.objects.create(bidder=user.username, auction=auction, price=price)

    crear_puja(admin, productos[0], 11)
    crear_puja(user1, productos[0], 14)
    crear_puja(user2, productos[0], 16)
    crear_puja(admin, productos[0], 20)

    crear_puja(user1, productos[1], 23)
    crear_puja(user2, productos[1], 25)

    crear_puja(user1, productos[2], 18)


def load_data_to_local_db(products):

    admin, user1, user2 = crear_usuarios()

    # CATEGORIAS
    categories = {}
    for product in products:
        category_name = product["category"]
        if category_name not in categories:
            category = Category.objects.create(name=category_name)
            categories[category_name] = category

    # PRODUCTOS
    productos = []
    for product in products:
        closing_date_naive = datetime(
            year=datetime.now().year,
            month=random.randint(5, 12),
            day=random.randint(1, 28),
            hour=0, minute=0, second=0
        )

        # Convertir el datetime naive a aware (con zona horaria)
        closing_date_aware = timezone.make_aware(closing_date_naive)
        auction = Auction.objects.create(
            title=product["title"],
            description=product["description"],
            closing_date=closing_date_aware,
            creation_date=datetime.now(),
            thumbnail=product["thumbnail"],
            price=product["price"],
            stock=product["stock"],
            rating=product["rating"],
            category=categories[product["category"]],
            brand=product.get("brand", "Desconocida"),
            auctioneer=admin
        )
        productos.append(auction)

    crear_pujas(productos, admin, user1, user2)

    print("Datos de dummyjson cargados a la BBDD")


if __name__ == "__main__":

    products_dummyjson = fetch_products()
    clear_sqlite_database()
    load_data_to_local_db(products_dummyjson)