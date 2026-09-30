import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker


fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Configuration
# -----------------------------

NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 200
NUM_ORDERS = 5000

CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Kitchen",
    "Books",
    "Beauty",
    "Sports",
]

PAYMENT_METHODS = [
    "Credit Card",
    "Debit Card",
    "UPI",
    "Net Banking",
    "Cash on Delivery",
]

ORDER_STATUSES = [
    "Completed",
    "Completed",
    "Completed",
    "Shipped",
    "Processing",
    "Cancelled",
]


# -----------------------------
# Helper
# -----------------------------

def write_csv(filename, rows, fieldnames):
    path = RAW_DIR / filename

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {filename}: {len(rows):,} records")


# -----------------------------
# Generate Customers
# -----------------------------

def generate_customers():
    customers = []

    for customer_id in range(1, NUM_CUSTOMERS + 1):
        email = fake.email()

        # Introduce some bad data
        if customer_id % 97 == 0:
            email = None

        if customer_id % 131 == 0:
            email = "invalid-email"

        customers.append({
            "customer_id": customer_id,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": email,
            "city": fake.city(),
            "state": fake.state(),
            "signup_date": fake.date_between(
                start_date="-3y",
                end_date="today"
            ).isoformat(),
        })

    # Add duplicate customers
    customers.extend(customers[:10])

    write_csv(
        "customers.csv",
        customers,
        [
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "city",
            "state",
            "signup_date",
        ],
    )


# -----------------------------
# Generate Products
# -----------------------------

def generate_products():
    products = []

    for product_id in range(1, NUM_PRODUCTS + 1):
        category = random.choice(CATEGORIES)

        products.append({
            "product_id": product_id,
            "product_name": f"{fake.word().title()} {fake.word().title()}",
            "category": category,
            "price": round(random.uniform(199, 50000), 2),
        })

    write_csv(
        "products.csv",
        products,
        [
            "product_id",
            "product_name",
            "category",
            "price",
        ],
    )

    return products


# -----------------------------
# Generate Orders + Items
# -----------------------------

def generate_orders(products):
    orders = []
    order_items = []

    start_date = datetime.now() - timedelta(days=730)

    for order_id in range(1, NUM_ORDERS + 1):

        customer_id = random.randint(1, NUM_CUSTOMERS)

        order_date = start_date + timedelta(
            days=random.randint(0, 729),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        status = random.choice(ORDER_STATUSES)

        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
        })

        # 1–5 products per order
        selected_products = random.sample(
            products,
            random.randint(1, 5)
        )

        for product in selected_products:
            quantity = random.randint(1, 5)

            # Introduce invalid quantity
            if order_id % 211 == 0:
                quantity = 0

            order_items.append({
                "order_item_id": len(order_items) + 1,
                "order_id": order_id,
                "product_id": product["product_id"],
                "quantity": quantity,
                "unit_price": product["price"],
            })

    write_csv(
        "orders.csv",
        orders,
        [
            "order_id",
            "customer_id",
            "order_date",
            "status",
        ],
    )

    write_csv(
        "order_items.csv",
        order_items,
        [
            "order_item_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
        ],
    )

    return orders


# -----------------------------
# Generate Payments
# -----------------------------

def generate_payments(orders):
    payments = []

    for order in orders:

        # Some cancelled orders won't have payments
        if order["status"] == "Cancelled" and random.random() < 0.7:
            continue

        payments.append({
            "payment_id": len(payments) + 1,
            "order_id": order["order_id"],
            "payment_method": random.choice(PAYMENT_METHODS),
            "payment_status": random.choice([
                "Success",
                "Success",
                "Success",
                "Failed",
            ]),
            "payment_date": order["order_date"],
        })

    write_csv(
        "payments.csv",
        payments,
        [
            "payment_id",
            "order_id",
            "payment_method",
            "payment_status",
            "payment_date",
        ],
    )


# -----------------------------
# Main
# -----------------------------

if __name__ == "__main__":
    print("\nGenerating e-commerce data...\n")

    generate_customers()

    products = generate_products()

    orders = generate_orders(products)

    generate_payments(orders)

    print("\nData generation completed successfully!")
    print(f"Raw data location: {RAW_DIR}")