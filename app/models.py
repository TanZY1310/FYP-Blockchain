#create three different users
from datetime import datetime
#from web.__init__ import db, login
from app import login, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), index=True, unique=True)
    email = db.Column(db.String(100), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # supplier = db.Column(db.Boolean, unique=False)

    role = db.Column(db.String (20), index=True) # test dropdown role 

    addresses = db.relationship('Address', backref = 'user', lazy = 'dynamic') #a user will have an address

    def __repr__(self): #how to print objects of this class - returns objects as strings
        return '<User {}>'.format(self.user_name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # def __init__(self, user_name, email):
    #     self.user_name = user_name
    #     self.email = email

class Address(db.Model):
    address_id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(128))
    city = db.Column(db.String(75))
    state = db.Column(db.String(75))
    zip_code = db.Column(db.String(16), index=True)
    country = db.Column(db.String(75))

    id =  db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Adress {}>'.format(self.street)

class Product(db.Model): #test product 
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(75), index=True)

    supplier_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    batches = db.relationship('Batch', backref='product', lazy='dynamic') #Lazy loading refers to objects are returned from a query without the related objects loaded at first

    def __repr__(self):
        return '<Product {}>'.format(self.product_name)

class Batch(db.Model):
    batch_id = db.Column(db.Integer, primary_key=True, index=True)
    # parent_batch_id = db.Column(db.Integer) #maybe can be used to identify who is the owner
    date_created = db.Column(db.String(8))

    # exp_date = db.Column(db.String(8))
    quantity = db.Column(db.Integer)

    supplier_id = db.Column(db.Integer, db.ForeignKey('user.id')) #test if can have multiple foreign keys

    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))

    def __repr__(self):
        return '<Batch {}>'.format(self.batch_id)   
    

#given a user ID, returns the associated user object
@login.user_loader
def load_actor(id):
    return User.query.get(int(id))