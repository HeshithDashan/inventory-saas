from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SECRET_KEY'] = 'sago-secret-key-123'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    items = db.relationship('BillItem', backref='bill', lazy=True)

class BillItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)

@app.route('/')
@login_required
def home():
    search_query = request.args.get('search')
    if search_query:
        products = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()
    else:
        products = Product.query.all()
    return render_template('dashboard.html', name=current_user.username, products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()

        if user_exists:
            flash('Username or Email already exists!')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created!')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Failed.')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        cost_price = request.form.get('cost_price')
        price = request.form.get('price')
        quantity = request.form.get('quantity')

        new_product = Product(name=name, cost_price=float(cost_price), price=float(price), quantity=int(quantity))
        
        db.session.add(new_product)
        db.session.commit()
        
        flash('Product added successfully!')
        return redirect(url_for('home'))

    return render_template('add_product.html')

@app.route('/edit-product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.name = request.form.get('name')
        product.cost_price = float(request.form.get('cost_price'))
        product.price = float(request.form.get('price'))
        product.quantity = int(request.form.get('quantity'))

        db.session.commit()
        flash('Product updated successfully!')
        return redirect(url_for('home'))

    return render_template('edit_product.html', product=product)

@app.route('/delete-product/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!')
    return redirect(url_for('home'))

@app.route('/billing')
@login_required
def billing():
    products = Product.query.all()
    products_json = [{'id': p.id, 'name': p.name, 'price': p.price, 'stock': p.quantity} for p in products]
    return render_template('billing.html', products=products, products_json=json.dumps(products_json))

@app.route('/save-bill', methods=['POST'])
@login_required
def save_bill():
    data = request.get_json()
    items = data.get('items')
    total_amount = data.get('total')

    if not items:
        return jsonify({'success': False, 'message': 'No items in bill'})

    new_bill = Bill(total_amount=total_amount)
    db.session.add(new_bill)
    db.session.flush()

    for item in items:
        product = Product.query.get(item['id'])
        if product:
            if product.quantity >= item['qty']:
                product.quantity -= item['qty']
                
                bill_item = BillItem(
                    bill_id=new_bill.id,
                    product_id=product.id,
                    product_name=product.name,
                    quantity=item['qty'],
                    price=item['price'],
                    total=item['total']
                )
                db.session.add(bill_item)
            else:
                return jsonify({'success': False, 'message': f'Not enough stock for {product.name}'})

    db.session.commit()
    return jsonify({'success': True, 'bill_id': new_bill.id})

@app.route('/reports')
@login_required
def reports():
    bills = Bill.query.order_by(Bill.date.desc()).all()
    total_revenue = sum(bill.total_amount for bill in bills)
    return render_template('reports.html', bills=bills, total_revenue=total_revenue)

@app.route('/view-bill/<int:id>')
@login_required
def view_bill(id):
    bill = Bill.query.get_or_404(id)
    return render_template('view_bill.html', bill=bill)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)