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
    print("Base de datos vaciada.")

def load_data_to_local_db(products):
    categories = {}
    for product in products:
        category_name = product["category"]
        if category_name not in categories:
            category = Category.objects.create(name=category_name)
            categories[category_name] = category

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
        )
    print("Datos de dummyjson cargados a la BBDD")


if __name__ == "__main__":

    products_dummyjson = fetch_products()
    clear_sqlite_database()
    load_data_to_local_db(products_dummyjson)