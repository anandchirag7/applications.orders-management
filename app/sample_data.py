from database import SessionLocal, engine, Base
from models import Product, Order
from datetime import datetime

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def insert_sample_data():
    db = SessionLocal()
    # Sample products
    products = [
        Product(sku="SKU001", name="Laptop", price=50000, stock=10),
        Product(sku="SKU002", name="Mouse", price=500, stock=100),
        Product(sku="SKU003", name="Keyboard", price=1500, stock=50),
    ]
    db.add_all(products)
    db.commit()
    # Sample orders
    orders = [
        Order(product_id=1, quantity=1, status="pending", created_at=datetime.utcnow()),
        Order(product_id=2, quantity=2, status="paid", created_at=datetime.utcnow()),
        Order(product_id=3, quantity=1, status="cancelled", created_at=datetime.utcnow()),
    ]
    db.add_all(orders)
    db.commit()
    db.close()
    print("Sample data inserted.")

if __name__ == "__main__":
    insert_sample_data()
