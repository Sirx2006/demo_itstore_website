from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ======================
# DATABASE
# ======================
def get_db():
    conn = sqlite3.connect('it_store.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # ตารางสินค้า
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        stock INTEGER
    )
    """)

    # ตารางตะกร้า
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER
    )
    """)

    conn.commit()
    conn.close()

# ======================
# ROUTES
# ======================

# หน้าแรก (แสดงสินค้า)
@app.route('/')
def index():
    conn = get_db()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template('index.html', products=products)

# เพิ่มสินค้า (ไว้ใช้เพิ่มข้อมูลเริ่มต้น)
@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    price = request.form['price']
    stock = request.form['stock']

    conn = get_db()
    conn.execute(
        "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
        (name, price, stock)
    )
    conn.commit()
    conn.close()

    return redirect('/')

# เพิ่มลงตะกร้า
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']

    conn = get_db()

    # เช็คว่ามีใน cart แล้วหรือยัง
    item = conn.execute(
        "SELECT * FROM cart WHERE product_id = ?",
        (product_id,)
    ).fetchone()

    if item:
        conn.execute(
            "UPDATE cart SET quantity = quantity + 1 WHERE product_id = ?",
            (product_id,)
        )
    else:
        conn.execute(
            "INSERT INTO cart (product_id, quantity) VALUES (?, 1)",
            (product_id,)
        )

    conn.commit()
    conn.close()

    return redirect('/')

# หน้าตะกร้า
@app.route('/cart')
def cart():
    conn = get_db()

    items = conn.execute("""
        SELECT products.product_id, products.name, products.price, cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.product_id
    """).fetchall()

    conn.close()

    # คำนวณราคารวม
    total = sum(item['price'] * item['quantity'] for item in items)

    return render_template('cart.html', items=items, total=total)

# ลบสินค้าออกจากตะกร้า
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = request.form['product_id']

    conn = get_db()
    conn.execute("DELETE FROM cart WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()

    return redirect('/cart')

# ล้างตะกร้า (checkout ง่ายๆ)
@app.route('/checkout', methods=['POST'])
def checkout():
    conn = get_db()
    conn.execute("DELETE FROM cart")
    conn.commit()
    conn.close()

    return redirect('/')

# ======================
# RUN APP
# ======================
if __name__ == '__main__':
    init_db()
    app.run(debug=True)