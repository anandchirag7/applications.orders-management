from flask import Flask, render_template_string, request, redirect, url_for
import requests

API_BASE = "http://127.0.0.1:8000"
app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Orders & Inventory UI</title>
</head>
<body>
    <h1>Products</h1>
    <form method="post" action="/add_product">
        SKU: <input name="sku" required>
        Name: <input name="name" required>
        Price: <input name="price" type="number" step="0.01" required>
        Stock: <input name="stock" type="number" required>
        <button type="submit">Add Product</button>
    </form>
    <ul>
    {% for p in products %}
        <li>{{p['id']}}: {{p['sku']}} - {{p['name']}} ({{p['price']}}) Stock: {{p['stock']}}</li>
    {% endfor %}
    </ul>
    <h1>Orders</h1>
    <form method="post" action="/add_order">
        Product ID: <input name="product_id" type="number" required>
        Quantity: <input name="quantity" type="number" required>
        Status: <select name="status">
            <option value="pending">pending</option>
            <option value="paid">paid</option>
            <option value="cancelled">cancelled</option>
        </select>
        <button type="submit">Add Order</button>
    </form>
    <ul>
    {% for o in orders %}
        <li>{{o['id']}}: Product {{o['product_id']}} Qty: {{o['quantity']}} Status: {{o['status']}}</li>
    {% endfor %}
    </ul>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    products = requests.get(f"{API_BASE}/products/").json()
    orders = requests.get(f"{API_BASE}/orders/").json()
    return render_template_string(TEMPLATE, products=products, orders=orders)

@app.route("/add_product", methods=["POST"])
def add_product():
    data = {
        "sku": request.form["sku"],
        "name": request.form["name"],
        "price": float(request.form["price"]),
        "stock": int(request.form["stock"])
    }
    requests.post(f"{API_BASE}/products/", json=data)
    return redirect(url_for("index"))

@app.route("/add_order", methods=["POST"])
def add_order():
    data = {
        "product_id": int(request.form["product_id"]),
        "quantity": int(request.form["quantity"]),
        "status": request.form["status"]
    }
    requests.post(f"{API_BASE}/orders/", json=data)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
