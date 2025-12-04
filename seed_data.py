from app import app, db, Product

def seed_products():
    with app.app_context():
        if Product.query.first():
            print("Products already exist!")
            return

        products = [
            Product(name="Milo (180ml)", cost_price=100.00, price=130.00, quantity=50),
            Product(name="CR Book (80 pgs)", cost_price=180.00, price=240.00, quantity=100),
            Product(name="Atlas Blue Pen", cost_price=30.00, price=45.00, quantity=200),
            Product(name="Pencil (HB)", cost_price=25.00, price=40.00, quantity=150),
            Product(name="Eraser (Maped)", cost_price=45.00, price=70.00, quantity=50),
            Product(name="Coca Cola (1.5L)", cost_price=350.00, price=420.00, quantity=20),
            Product(name="Anchor Milk Powder (400g)", cost_price=1050.00, price=1200.00, quantity=15),
            Product(name="Panadol Card", cost_price=40.00, price=60.00, quantity=100),
            Product(name="Samaposha (200g)", cost_price=150.00, price=190.00, quantity=40),
            Product(name="Munchee Super Cream Cracker", cost_price=420.00, price=510.00, quantity=25),
            Product(name="Lifebuoy Soap", cost_price=110.00, price=140.00, quantity=60),
            Product(name="Signal Toothpaste (120g)", cost_price=220.00, price=275.00, quantity=30),
            Product(name="A4 Paper Bundle (500)", cost_price=2100.00, price=2600.00, quantity=3),
            Product(name="Sunlight Powder (1kg)", cost_price=550.00, price=680.00, quantity=20),
            Product(name="Keerisamba Rice (1kg)", cost_price=280.00, price=320.00, quantity=50)
        ]

        db.session.bulk_save_objects(products)
        db.session.commit()
        print("Sample products added successfully!")

if __name__ == '__main__':
    seed_products()