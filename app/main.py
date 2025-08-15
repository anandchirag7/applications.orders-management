from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine, Base
from fastapi.responses import JSONResponse

Base.metadata.create_all(bind=engine)
app = FastAPI()
@app.get("/")
def root():
    return JSONResponse(content={
        "message": "Welcome to the Orders & Inventory API!",
        "endpoints": [
            {"path": "/products/", "methods": ["GET", "POST"]},
            {"path": "/products/{product_id}", "methods": ["GET", "PUT", "DELETE"]},
            {"path": "/orders/", "methods": ["GET", "POST"]},
            {"path": "/orders/{order_id}", "methods": ["GET", "PUT", "DELETE"]}
        ],
        "docs": "Visit /docs for interactive API documentation and to try all endpoints."
    })

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db, product)

@app.get("/products/", response_model=list[schemas.Product])
def list_products(db: Session = Depends(get_db)):
    return crud.get_products(db)

@app.get("/products/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = crud.update_product(db, product_id, product)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.delete_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"ok": True}

@app.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    product = crud.get_product(db, order.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < order.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")
    # Only reduce stock if order is immediately paid
    if order.status == "paid":
        product.stock -= order.quantity
        db.commit()
        db.refresh(product)
    db_order = crud.create_order(db, order)
    return db_order
# Add webhook endpoint to mark order as paid and update product stock
@app.post("/orders/{order_id}/mark_paid")
def mark_order_paid(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    if db_order.status != "paid":
        product = crud.get_product(db, db_order.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        if product.stock < db_order.quantity:
            raise HTTPException(status_code=400, detail="Not enough stock")
        product.stock -= db_order.quantity
        db_order.status = "paid"
        db.commit()
        db.refresh(product)
        db.refresh(db_order)
    return {"ok": True, "order_id": order_id, "status": db_order.status}

@app.get("/orders/", response_model=list[schemas.Order])
def list_orders(db: Session = Depends(get_db)):
    return crud.get_orders(db)

@app.get("/orders/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.put("/orders/{order_id}", response_model=schemas.Order)
def update_order(order_id: int, order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = crud.update_order(db, order_id, order)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.delete_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"ok": True}

@app.post("/orders/{order_id}/mark_paid")
def mark_order_paid(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db_order.status = "paid"
    db.commit()
    db.refresh(db_order)
    return {"ok": True, "order_id": order_id, "status": db_order.status}


