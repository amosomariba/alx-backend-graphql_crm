# seed_db.py
import os
import django
import random
from decimal import Decimal
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_customers():
    customers = [
        {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol", "email": "carol@example.com"},
    ]

    for data in customers:
        Customer.objects.get_or_create(email=data["email"], defaults=data)
    print(f"✅ Seeded {len(customers)} customers.")

def seed_products():
    products = [
        {"name": "Laptop", "price": Decimal("999.99"), "stock": 10},
        {"name": "Mouse", "price": Decimal("25.50"), "stock": 50},
        {"name": "Keyboard", "price": Decimal("45.00"), "stock": 30},
    ]

    for data in products:
        Product.objects.get_or_create(name=data["name"], defaults=data)
    print(f"✅ Seeded {len(products)} products.")

def seed_orders():
    customers = list(Customer.objects.all())
    products = list(Product.objects.all())

    if not customers or not products:
        print("⚠️ Cannot seed orders — missing customers or products.")
        return

    for i in range(3):
        customer = random.choice(customers)
        selected_products = random.sample(products, k=2)
        total_amount = sum(p.price for p in selected_products)

        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=timezone.now()
        )
        order.products.set(selected_products)
    print("✅ Seeded 3 orders.")

if __name__ == "__main__":
    seed_customers()
    seed_products()
    seed_orders()
    print("🌱 Database seeded successfully.")
