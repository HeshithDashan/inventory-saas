import os
import secrets
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, current_app, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
from collections import defaultdict
from flask_mail import Mail, Message
import random
from functools import wraps
import pandas as pd
from io import BytesIO
from sqlalchemy import func

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SECRET_KEY'] = 'sago-secret-key-123'
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'heshithdashan24@gmail.com'
app.config['MAIL_PASSWORD'] = 'ghfp srlj nbkb yhsu'
app.config['MAIL_DEFAULT_SENDER'] = 'heshithdashan24@gmail.com'

mail = Mail(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_store_details():
    store = StoreSettings.query.first()
    if not store:
        store = StoreSettings(
            shop_name='My Shop',
            address='',
            phone='',
            header_text='Welcome',
            footer_text='Thank You'
        )
        db.session.add(store)
        db.session.commit()
    return dict(store=store)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('You do not have permission to access this page.')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='cashier')
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    barcode = db.Column(db.String(50), nullable=True)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    company = db.Column(db.String(150), nullable=True)
    bills = db.relationship('SupplierBill', backref='supplier', lazy=True)
    payments = db.relationship('SupplierPayment', backref='supplier', lazy=True)

class SupplierBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    note = db.Column(db.String(200), nullable=True)

class SupplierPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    note = db.Column(db.String(200), nullable=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

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

class StoreSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_name = db.Column(db.String(150), nullable=True)
    address = db.Column(db.String(250), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    header_text = db.Column(db.String(100), nullable=True)
    footer_text = db.Column(db.String(100), nullable=True)

class Return(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    amount_refunded = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(200), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Damage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    loss_amount = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(200), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)



@app.route('/')
@login_required
def home():
    low_stock_products = Product.query.filter(Product.quantity <= 5).all()
    
    search_query = request.args.get('search')
    if search_query:
        products = Product.query.filter(
            (Product.name.ilike(f'%{search_query}%')) | 
            (Product.barcode.ilike(f'%{search_query}%'))
        ).all()
    else:
        products = Product.query.order_by(Product.id.desc()).all()
        
    return render_template('dashboard.html', user=current_user, products=products, low_stock_products=low_stock_products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()

        if user_exists:
            flash('Username or Email already exists!')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_user = User(username=username, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created! You can now login.')
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

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            otp = random.randint(100000, 999999)
            session['reset_otp'] = otp
            session['reset_email'] = email
            
            try:
                msg = Message('Password Reset Code', recipients=[email])
                msg.body = f'Your OTP is: {otp}'
                mail.send(msg)
                flash('OTP sent to your email!')
            except Exception as e:
                print(f"Error: {e}")
                flash('Email failed. Check terminal for OTP.')
            
            return redirect(url_for('verify_otp'))
        else:
            flash('Email not found!')
    return render_template('forgot_password.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reset_otp' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        otp_input = request.form.get('otp')
        if otp_input and otp_input.isdigit() and int(otp_input) == session.get('reset_otp'):
            session['verified_reset'] = True
            return redirect(url_for('reset_new_password'))
        else:
            flash('Invalid OTP!')
    return render_template('verify_otp.html')

@app.route('/reset-new-password', methods=['GET', 'POST'])
def reset_new_password():
    if 'verified_reset' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        password = request.form.get('password')
        email = session['reset_email']
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
            db.session.commit()
            session.pop('reset_otp', None)
            session.pop('reset_email', None)
            session.pop('verified_reset', None)
            flash('Password reset successful!')
            return redirect(url_for('login'))
    
    return render_template('reset_password.html')

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
        barcode = request.form.get('barcode')
        cost_price = request.form.get('cost_price')
        price = request.form.get('price')
        quantity = request.form.get('quantity')

        new_product = Product(
            name=name, 
            barcode=barcode,
            cost_price=float(cost_price), 
            price=float(price), 
            quantity=int(quantity)
        )
        
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
        product.barcode = request.form.get('barcode')
        product.cost_price = float(request.form.get('cost_price'))
        product.price = float(request.form.get('price'))
        product.quantity = int(request.form.get('quantity'))

        db.session.commit()
        flash('Product updated successfully!')
        return redirect(url_for('home'))

    return render_template('edit_product.html', product=product)

@app.route('/delete-product/<int:id>')
@login_required
@admin_required
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
    products_json = [{'id': p.id, 'name': p.name, 'price': p.price, 'stock': p.quantity, 'barcode': p.barcode} for p in products]
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
@admin_required
def reports():
    bills = Bill.query.order_by(Bill.date.desc()).all()
    total_revenue = sum(bill.total_amount for bill in bills)

    sales_data = defaultdict(float)
    for bill in bills:
        date_str = bill.date.strftime('%Y-%m-%d')
        sales_data[date_str] += bill.total_amount

    expenses = Expense.query.all()
    total_expenses = sum(exp.amount for exp in expenses)
    
    expense_cats = defaultdict(float)
    for exp in expenses:
        expense_cats[exp.category] += exp.amount

    net_profit = total_revenue - total_expenses

    sorted_dates = sorted(sales_data.keys())
    chart_labels = sorted_dates
    chart_values = [sales_data[date] for date in sorted_dates]
    
    exp_labels = list(expense_cats.keys())
    exp_values = list(expense_cats.values())

    top_items = db.session.query(
        BillItem.product_name, 
        func.sum(BillItem.quantity).label('total_qty')
    ).group_by(BillItem.product_name).order_by(func.sum(BillItem.quantity).desc()).limit(5).all()

    top_product_names = [item[0] for item in top_items]
    top_product_values = [item[1] for item in top_items]

    return render_template('reports.html', 
                           bills=bills, 
                           total_revenue=total_revenue,
                           total_expenses=total_expenses,
                           net_profit=net_profit,
                           chart_labels=json.dumps(chart_labels),
                           chart_values=json.dumps(chart_values),
                           exp_labels=json.dumps(exp_labels),
                           exp_values=json.dumps(exp_values),
                           top_product_names=json.dumps(top_product_names),
                           top_product_values=json.dumps(top_product_values))

@app.route('/export-excel')
@login_required
@admin_required
def export_excel():
    bills = Bill.query.order_by(Bill.date.desc()).all()
    data = []
    for bill in bills:
        data.append({
            'Bill ID': bill.id,
            'Date': bill.date.strftime('%Y-%m-%d %H:%M:%S'),
            'Total Amount': bill.total_amount,
            'Item Count': len(bill.items)
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sales Report')
    
    output.seek(0)
    return send_file(output, download_name="Sales_Report.xlsx", as_attachment=True)

@app.route('/backup')
@login_required
@admin_required
def backup_database():
    db_path = os.path.join(app.instance_path, 'inventory.db')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(db_path, as_attachment=True, download_name=f"backup_{timestamp}.db")

@app.route('/restore', methods=['POST'])
@login_required
@admin_required
def restore_backup():
    if 'backup_file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('settings'))
    
    file = request.files['backup_file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('settings'))

    if file:
        try:
            db_path = os.path.join(app.instance_path, 'inventory.db')
            file.save(db_path)
            flash('Database restored successfully! Please log in again.', 'success')
            return redirect(url_for('settings'))
        except Exception as e:
            flash(f'Error restoring database: {str(e)}', 'error')
            return redirect(url_for('settings'))
            
    return redirect(url_for('settings'))

@app.route('/view-bill/<int:id>')
@login_required
def view_bill(id):
    bill = Bill.query.get_or_404(id)
    return render_template('view_bill.html', bill=bill, user=current_user)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    store = StoreSettings.query.first()
    if not store:
        store = StoreSettings(shop_name="My Shop", address="", phone="", header_text="Welcome", footer_text="Thank you")
        db.session.add(store)
        db.session.commit()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            new_username = request.form.get('username')
            new_email = request.form.get('email')
            
            if request.files.get('picture'):
                picture_file = save_picture(request.files['picture'])
                current_user.image_file = picture_file

            existing_user = User.query.filter(((User.username == new_username) | (User.email == new_email)) & (User.id != current_user.id)).first()
            
            if existing_user:
                flash('Username or Email already taken!')
            else:
                current_user.username = new_username
                current_user.email = new_email
                db.session.commit()
                flash('Profile updated successfully!')
                
        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            
            if not check_password_hash(current_user.password, current_password):
                flash('Incorrect current password!')
            else:
                current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
                db.session.commit()
                flash('Password changed successfully!')
        
        elif action == 'update_store':
            if current_user.role != 'admin':
                flash('Only admins can change store settings!')
            else:
                store.shop_name = request.form.get('shop_name')
                store.address = request.form.get('address')
                store.phone = request.form.get('phone')
                store.header_text = request.form.get('header_text')
                store.footer_text = request.form.get('footer_text')
                
                db.session.commit()
                flash('Store settings updated successfully!')
                
        return redirect(url_for('settings'))
        
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('settings.html', user=current_user, image_file=image_file, store=store)

@app.route('/suppliers', methods=['GET', 'POST'])
@login_required
@admin_required
def suppliers():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_supplier':
            name = request.form.get('name')
            mobile = request.form.get('mobile')
            company = request.form.get('company')
            
            new_supplier = Supplier(name=name, mobile=mobile, company=company)
            db.session.add(new_supplier)
            db.session.commit()
            flash('Supplier added successfully!')
            
        elif action == 'add_bill':
            supplier_id = request.form.get('supplier_id')
            amount = request.form.get('amount')
            note = request.form.get('note')
            
            new_bill = SupplierBill(supplier_id=supplier_id, amount=float(amount), note=note)
            db.session.add(new_bill)
            db.session.commit()
            flash('Bill recorded (Added to Debt)!')

        elif action == 'add_payment':
            supplier_id = request.form.get('supplier_id')
            amount = request.form.get('amount')
            note = request.form.get('note')
            
            new_payment = SupplierPayment(supplier_id=supplier_id, amount=float(amount), note=note)
            db.session.add(new_payment)
            db.session.commit()
            flash('Payment recorded (Deducted from Debt)!')
            
        return redirect(url_for('suppliers'))
    
    suppliers_list = Supplier.query.order_by(Supplier.id.desc()).all()
    
    supplier_data = []
    
    for s in suppliers_list:
        total_billed = sum(bill.amount for bill in s.bills)
        total_paid = sum(pay.amount for pay in s.payments)
        due_amount = total_billed - total_paid
        
        history = []
        for b in s.bills:
            history.append({'date': b.date, 'type': 'Bill', 'amount': b.amount, 'note': b.note})
        for p in s.payments:
            history.append({'date': p.date, 'type': 'Payment', 'amount': p.amount, 'note': p.note})
        
        history.sort(key=lambda x: x['date'], reverse=True)

        last_entry = history[0] if history else None
        last_date = last_entry['date'].strftime('%Y-%m-%d') if last_entry else "No Activity"

        supplier_data.append({
            'id': s.id,
            'name': s.name,
            'mobile': s.mobile,
            'company': s.company,
            'total_billed': total_billed,
            'total_paid': total_paid,
            'due_amount': due_amount,
            'last_date': last_date,
            'history': history
        })

    return render_template('suppliers.html', suppliers=supplier_data)

@app.route('/delete-supplier/<int:id>')
@login_required
@admin_required
def delete_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    SupplierBill.query.filter_by(supplier_id=id).delete()
    SupplierPayment.query.filter_by(supplier_id=id).delete()
    db.session.delete(supplier)
    db.session.commit()
    flash('Supplier and all history deleted successfully!')
    return redirect(url_for('suppliers'))

@app.route('/expenses', methods=['GET', 'POST'])
@login_required
@admin_required
def expenses():
    if request.method == 'POST':
        category = request.form.get('category')
        description = request.form.get('description')
        amount = request.form.get('amount')
        date_str = request.form.get('date')

        if date_str:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date_obj = datetime.utcnow()

        new_expense = Expense(category=category, description=description, amount=float(amount), date=date_obj)
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense added successfully!')
        return redirect(url_for('expenses'))

    expenses_list = Expense.query.order_by(Expense.date.desc()).all()

    today = datetime.today().date()
    current_month_start = datetime.today().replace(day=1, hour=0, minute=0, second=0)

    total_expenses_all = sum(exp.amount for exp in expenses_list)
    total_expenses_month = sum(exp.amount for exp in expenses_list if exp.date >= current_month_start)
    total_expenses_today = sum(exp.amount for exp in expenses_list if exp.date.date() == today)

    cat_totals = defaultdict(float)
    for exp in expenses_list:
        cat_totals[exp.category] += exp.amount
    
    chart_labels = list(cat_totals.keys())
    chart_values = list(cat_totals.values())

    return render_template('expenses.html', 
                           expenses=expenses_list,
                           total_all=total_expenses_all,
                           total_month=total_expenses_month,
                           total_today=total_expenses_today,
                           chart_labels=json.dumps(chart_labels),
                           chart_values=json.dumps(chart_values))

@app.route('/delete-expense/<int:id>')
@login_required
@admin_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!')
    return redirect(url_for('expenses'))


@app.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/add-user', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    user_exists = User.query.filter((User.username == username) | (User.email == email)).first()

    if user_exists:
        flash('Username or Email already exists!')
    else:
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash(f'New {role} added successfully!')
    
    return redirect(url_for('manage_users'))

@app.route('/delete-user/<int:id>')
@login_required
@admin_required
def delete_user(id):
    if id == current_user.id:
        flash('You cannot delete your own account!')
    else:
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!')
        
    return redirect(url_for('manage_users'))

@app.route('/admin-reset-password', methods=['POST'])
@login_required
@admin_required
def admin_reset_password():
    user_id = request.form.get('user_id')
    new_password = request.form.get('new_password')
    
    user = User.query.get(user_id)
    if user:
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash(f'Password for {user.username} reset successfully!')
    else:
        flash('User not found!')
        
    return redirect(url_for('manage_users'))


@app.route('/returns-damages')
@login_required
def returns_damages_page():

    products = Product.query.all()
    
    recent_returns = Return.query.order_by(Return.date.desc()).limit(50).all()
    recent_damages = Damage.query.order_by(Damage.date.desc()).limit(50).all()
    
    return render_template('returns_damages.html', products=products, returns=recent_returns, damages=recent_damages)

@app.route('/add-return', methods=['POST'])
@login_required
def add_return():
    product_id = request.form.get('product_id')
    qty = int(request.form.get('quantity'))
    refund = float(request.form.get('amount_refunded'))
    reason = request.form.get('reason')

    product = Product.query.get(product_id)
    if product:

        product.quantity += qty
        
        new_return = Return(product_id=product.id, product_name=product.name, quantity=qty, amount_refunded=refund, reason=reason)
        db.session.add(new_return)
        db.session.commit()
        flash('Return processed successfully! Stock updated.')
    else:
        flash('Product not found!')
    
    return redirect(url_for('returns_damages_page'))

@app.route('/add-damage', methods=['POST'])
@login_required
def add_damage():
    product_id = request.form.get('product_id')
    qty = int(request.form.get('quantity'))
    note = request.form.get('note')

    product = Product.query.get(product_id)
    if product:
        if product.quantity >= qty:

            product.quantity -= qty
            
            loss = product.cost_price * qty

            new_damage = Damage(product_id=product.id, product_name=product.name, quantity=qty, loss_amount=loss, note=note)
            db.session.add(new_damage)
            db.session.commit()
            flash('Damage recorded! Stock deducted.')
        else:
            flash(f'Error: Not enough stock for {product.name}!')
    else:
        flash('Product not found!')
    
    return redirect(url_for('returns_damages_page'))

@app.route('/barcode-labels')
@login_required
def barcode_labels():
    products = Product.query.order_by(Product.name).all()
    return render_template('barcode_labels.html', products=products)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)