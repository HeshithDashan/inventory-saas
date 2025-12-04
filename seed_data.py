from app import app, db, Product

def seed_products():
    with app.app_context():

        if Product.query.first():
            print("Products already exist! Delete inventory.db to re-seed.")
            return

        products = [

            Product(name="Milo (180ml)", cost_price=100.00, price=130.00, quantity=50),
            Product(name="Coca Cola (1.5L)", cost_price=350.00, price=420.00, quantity=20),
            Product(name="EGB (Elephant House) 1.5L", cost_price=340.00, price=400.00, quantity=25),
            Product(name="Cream Soda 1.5L", cost_price=340.00, price=400.00, quantity=30),
            Product(name="Pepsi (1.5L)", cost_price=350.00, price=420.00, quantity=15),
            Product(name="Smak Woodapple Nectar", cost_price=80.00, price=110.00, quantity=60),
            Product(name="Highland Milk Packet (Choc)", cost_price=75.00, price=95.00, quantity=100),
            Product(name="Kotmale Vanilla Milk", cost_price=80.00, price=100.00, quantity=80),
            Product(name="Nescafe 3-in-1 Packet", cost_price=45.00, price=60.00, quantity=200),
            Product(name="Anchor Milk Powder (400g)", cost_price=1050.00, price=1200.00, quantity=15),
            Product(name="Raththi Milk Powder (400g)", cost_price=1000.00, price=1150.00, quantity=20),
            Product(name="Watawala Tea (200g)", cost_price=450.00, price=550.00, quantity=30),
            Product(name="Laojee Tea (100g)", cost_price=270.00, price=340.00, quantity=35),

            Product(name="Munchee Super Cream Cracker", cost_price=420.00, price=510.00, quantity=25),
            Product(name="Maliban Marie Biscuit", cost_price=250.00, price=320.00, quantity=40),
            Product(name="Munchee Lemon Puff", cost_price=300.00, price=380.00, quantity=35),
            Product(name="Maliban Chocolate Biscuit", cost_price=280.00, price=350.00, quantity=50),
            Product(name="Munchee Nice Biscuit", cost_price=240.00, price=300.00, quantity=30),
            Product(name="Kandos Chocolate (45g)", cost_price=150.00, price=190.00, quantity=60),
            Product(name="Ritzbury Chit Chat", cost_price=60.00, price=80.00, quantity=100),
            Product(name="Tipi Tip (Onion)", cost_price=50.00, price=70.00, quantity=80),
            Product(name="Samaposha (200g)", cost_price=150.00, price=190.00, quantity=40),

            Product(name="Keerisamba Rice (1kg)", cost_price=280.00, price=320.00, quantity=50),
            Product(name="Nadu Rice (1kg)", cost_price=210.00, price=240.00, quantity=100),
            Product(name="Samba Rice (1kg)", cost_price=230.00, price=260.00, quantity=80),
            Product(name="Basmati Rice (1kg)", cost_price=550.00, price=700.00, quantity=20),
            Product(name="Red Raw Rice (1kg)", cost_price=190.00, price=220.00, quantity=60),
            Product(name="Wheat Flour (1kg)", cost_price=220.00, price=260.00, quantity=50),
            Product(name="White Sugar (1kg)", cost_price=280.00, price=330.00, quantity=70),
            Product(name="Dhal (Mysore) 500g", cost_price=180.00, price=220.00, quantity=40),
            Product(name="Maggi Noodles (Chicken)", cost_price=130.00, price=165.00, quantity=150),
            Product(name="Prima Kottu Mee (Hot & Spicy)", cost_price=140.00, price=180.00, quantity=100),
            Product(name="Canned Fish (Large)", cost_price=650.00, price=850.00, quantity=30),
            Product(name="Soya Meat (Chicken)", cost_price=80.00, price=110.00, quantity=60),

            Product(name="Chilli Powder (100g)", cost_price=150.00, price=200.00, quantity=50),
            Product(name="Curry Powder (100g)", cost_price=140.00, price=190.00, quantity=50),
            Product(name="Turmeric Powder (50g)", cost_price=100.00, price=140.00, quantity=40),
            Product(name="Salt Packet (400g)", cost_price=70.00, price=100.00, quantity=60),
            Product(name="Coconut Oil (1L)", cost_price=650.00, price=800.00, quantity=25),

            Product(name="Lifebuoy Soap", cost_price=110.00, price=140.00, quantity=60),
            Product(name="Lux Soap (Pink)", cost_price=120.00, price=160.00, quantity=50),
            Product(name="Dettol Soap", cost_price=130.00, price=170.00, quantity=45),
            Product(name="Signal Toothpaste (120g)", cost_price=220.00, price=275.00, quantity=30),
            Product(name="Clogard Toothpaste (120g)", cost_price=210.00, price=260.00, quantity=30),
            Product(name="Sunsilk Shampoo (180ml)", cost_price=450.00, price=580.00, quantity=20),
            Product(name="Panadol Card", cost_price=40.00, price=60.00, quantity=100),
            Product(name="Siddhalepa Balm", cost_price=180.00, price=220.00, quantity=40),

            Product(name="Sunlight Powder (1kg)", cost_price=550.00, price=680.00, quantity=20),
            Product(name="Rin Washing Powder (1kg)", cost_price=480.00, price=600.00, quantity=25),
            Product(name="Vim Dishwash Bar", cost_price=90.00, price=120.00, quantity=60),
            Product(name="Harpic Toilet Cleaner", cost_price=400.00, price=520.00, quantity=15),
            Product(name="Matches (Box)", cost_price=20.00, price=25.00, quantity=20),
            Product(name="Mosquito Coil Packet", cost_price=180.00, price=240.00, quantity=50),

            Product(name="CR Book (80 pgs)", cost_price=180.00, price=240.00, quantity=100),
            Product(name="CR Book (120 pgs)", cost_price=250.00, price=320.00, quantity=80),
            Product(name="Exercise Book (80 pgs)", cost_price=80.00, price=120.00, quantity=150),
            Product(name="Atlas Blue Pen", cost_price=30.00, price=45.00, quantity=200),
            Product(name="Atlas Black Pen", cost_price=30.00, price=45.00, quantity=100),
            Product(name="Atlas Red Pen", cost_price=30.00, price=45.00, quantity=50),
            Product(name="Pencil (HB)", cost_price=25.00, price=40.00, quantity=150),
            Product(name="Eraser (Maped)", cost_price=45.00, price=70.00, quantity=50),
            Product(name="A4 Paper Bundle (500)", cost_price=2100.00, price=2600.00, quantity=3),
            Product(name="Ruler (30cm)", cost_price=40.00, price=60.00, quantity=60),
            Product(name="Glue Bottle (Small)", cost_price=80.00, price=110.00, quantity=40)
        ]

        db.session.bulk_save_objects(products)
        db.session.commit()
        print(f"Successfully added {len(products)} products!")

if __name__ == '__main__':
    seed_products()