from contextlib import redirect_stderr
from datetime import timedelta
import datetime as dt
from itertools import product
import json
from pickle import FALSE

from uuid import uuid4

import requests
from flask import Flask, jsonify, render_template, request, url_for, redirect, session, flash

from sqlalchemy.exc import IntegrityError

#forms/logins/db
from app.forms import LoginForm, RegistrationForm, ProductForm, BatchForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User, Address, Product, Batch
from app import app, db

from url_parser import parse_url

#Initialize blockchain object
from blockchain import Block, Blockchain

#test store mongodb
from mongosample import collection


blockchain = Blockchain()


# Set the node address, can have multiple nodes
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

transactions = []

transactions_users=[]

errors = []

supplier = True


@app.errorhandler(404) #not sure if needed
def not_found_error(error):
    return render_template('error404.html'), 404

"""
Not needed
"""

# @app.route('/update_connected_node_address/<address>') #not sure if needed
# def update_connected_node_address(address):
#     """
#     Route to change the currently connected node
#     """
#     #TODO update these method 

#     global CONNECTED_NODE_ADDRESS
#     #CONNECTED_NODE_ADDRESS = "http://127.0.0.1:" + str(address) + "/"
#     return "Success"

"""
User Management
"""
@app.route('/signup', methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(user_name=form.user_name.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush() #get id of user

        address = Address(street = form.street.data, city=form.city.data, state=form.state.data, zip_code=form.zip_code.data, country=form.country.data, id=user.id)
        db.session.add(address)
        db.session.commit()
        flash(f'User has been registered and added into database!', 'info')

        login_user(user, remember=True)

        return redirect(url_for('home'))

    else:
        flash(f"User could not be registered, Please try agin", 'info')
    
    return render_template('signup.html',  title='Sign Up', form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.user_name.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid user name or password', 'info')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or parse_url(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)

    else:
        flash(f"Log in failed, Please try again", 'info')

    return render_template('login.html', title='Sign In', form=form)

@app.route("/logout")
def logout():
    flash(f"You have been logged out!", "info") #the info have different built in category (warning, info, error, etc)
    
    logout_user()
    return redirect(url_for('home'))

"""
User Profiles
"""
@app.route('/user/<user_name>')
@login_required
def user(user_name):
    user = User.query.filter_by(user_name=user_name).first_or_404()
    address = Address.query.filter_by(id=user.id).first()
    return render_template( 'user.html',
                            title=user.user_name,
                            user=user,
                            supplier=supplier,
                            address=address)

# @app.route('/update_user', methods=['GET', 'POST']) # function to update user
# @login.required
# def update_product():
#     product_to_update = Product.Query.get_or_404()

@app.route('/userID/<user_id>')
def userID(user_id):
    """
    Return the user page for an user of the blockchain using the user id (an int)
    """
    user = User.query.filter_by(id=user_id).first_or_404()
    address = Address.query.filter_by(id=user_id).first()
    return render_template( 'user.html',
                            title=user.user_name,
                            user=user,
                            supplier=supplier,
                            address=address)

"""
Product
"""
@app.route('/new_product', methods=['GET', 'POST'])
@login_required
def new_product():
    """
    Route to add a new product to the blockchain
    """
    if request.method == 'POST':
        if request.form['product_name']=='':
            flash('Missing data', 'info')
        else:
            try:
                product=Product(product_name=request.form['product_name'], supplier_id=current_user.id) 
                db.session.add(product)
                db.session.commit()
                flash('Product has been added.', 'info')

            except IntegrityError:
                flash('This product already exist.', 'error')

                return redirect(url_for('user_product'))

    return redirect(url_for('user_product'))

@app.route('/delete_product/<int:product_id>') # function to delete existing product
@login_required
def delete_product(product_id):
    product_to_delete = Product.query.get_or_404(product_id)
    
    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        flash('Product has been deleted.', 'info')

    except:
        flash('There was a problem deleting the product.', 'info')

    return redirect(url_for('user_product'))

@app.route('/user_product')
@login_required
def user_product():
    """
    List all the product of the currently connected user - only applicable to supplier
    """

    products = Product.query.filter_by(supplier_id=current_user.id).all()

    return render_template('user_product.html',
                           title='Data of an user stock',
                        #    transactions=transactions_user,
                           products=products,
                           supplier=supplier,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string,
                        #    user_id=user_id,
                           errors=errors)

@app.route('/fetchproduct_for_user_id', methods=['POST'])
@login_required
def fetch_product_for_user_id():
    """
    Route to get all the product for a given user_id
    """
    user_id = current_user.id

    return redirect(url_for('user_product'))


"""
Batch
"""
@app.route('/new_batch', methods=['POST'])
@login_required
def new_batch():
    """
    Route to create a new batch
    """
    if request.method == 'POST':
        if request.form['date_created']=='' or request.form['quantity']=='':
            flash('Not enough details')
        else:
            batch=Batch(date_created=request.form['date_created'], product_id=request.form['product_id'], quantity=request.form['quantity'], supplier_id=current_user.id)
            db.session.add(batch)
            db.session.flush()
            db.session.commit()

            json_object = {
                'batch_id': int(batch.batch_id),
                'sender_id': int(current_user.id),
                'quantity': int(request.form['quantity'])
            }

            new_batch_address="{}/register_batch".format(CONNECTED_NODE_ADDRESS) #might be removed because seems redundant and replace with another transaction by distributor to retailer
            requests.post(new_batch_address,
                          json=json_object,
                          headers={'Content-type': 'application/json'})

            flash('New batch created', 'info')

            # return redirect(url_for('user_batch'))

    return redirect(url_for('home'))

@app.route('/delete_batch/<int:batch_id>') # function to delete existing batch
@login_required
def delete_batch(batch_id):
    batch_to_delete = Batch.query.get_or_404(batch_id)

    try:
        db.session.delete(batch_to_delete)
        db.session.commit()
        flash('Batch has been deleted.', 'info')

    except:
        flash('There was a problem deleting the batch.', 'info')

    return redirect(url_for('user_batch'))

@app.route('/fetchbatch_for_user_id', methods=['POST']) #might not be needed
@login_required
def fetch_batch_for_user_id():
    """
    Route to get all the batches for a given user_id
    """
    user_id = current_user.id

    return redirect(url_for('user_batch'))

@app.route('/user_batch')
@login_required
def user_batch():
    """
    List all the batch of the currently connected user - only applicable to supplier
    """
    # transactions = fetch_transactions_without_double() replaced with fetch()_transactions

    users = User.query.filter_by(role = "Distributor").all() #get all user id that is distributor

    batches = Batch.query.filter_by(supplier_id=current_user.id).all() #try to filter based on supplier id so different supplier wont show all the batches

    return render_template('user_batch.html',
                           title='Data of batches created',
                           #transactions=transactions_user,
                           batches=batches,
                           users=users,
                           supplier=supplier,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string,
                           errors=errors)

@app.route('/send_batch', methods=["POST"]) # for supplier to send batch to distributor
@login_required
def send_batch():
    #global transactions_users
    # transactions = []
    transactions = fetch_current_user_transactions() 

    if request.method == "POST":
        if request.form['batch_id'] == '':
            flash('Missing Data', 'info')
        else:
            user_owner_batch = FALSE
            for t in transactions:           
                if int(request.form['batch_id']) == int(t['batch_id']): #compare batch id with id in list of transactions to prove owner of batch
                    user_owner_batch = True
                    #batches= Batch.query.filter_by(batch_id=request.form['batch_id']).first_or_404()

            if user_owner_batch:
                batches= Batch.query.filter_by(batch_id=request.form['batch_id']).first_or_404()
                json_object = {
                            'batch_id': int(request.form['batch_id']),
                            'sender_id': int(current_user.id),
                            'recipient_id': int(request.form['recipient_id']),
                            'quantity': int(batches.quantity),
                            'status': request.form['statusTransaction']
                        }

                new_transaction_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)
                requests.post(  new_transaction_address,
                                json=json_object,
                                headers={'Content-type': 'application/json'})             

                #mine_blockchain() #add to blochain
                flash('Batch has been sent to distributor', 'info')
                flash('Blockchain created', 'info')

                # return render_template('user_batch.html', batch_id=batch_id)
            else:
                flash('You are not the owner of the batch', 'error')

            return redirect(url_for('home')) #send to home page immediately so that user can mine block

@app.route('/send_to_retailer', methods=['POST'])
def send_to_retailer():

    # transactions = fetch_transactions()

    if request.method == 'POST':
        if request.form['recipient_id']=='':
            flash('Missing Data', 'info')
        
        else:
            batches= Batch.query.filter_by(batch_id=request.form['batch_id']).first_or_404()
            json_object = {
                            'batch_id': int(request.form['batch_id']),
                            'sender_id': int(current_user.id),
                            'recipient_id': int(request.form['recipient_id']),
                            'quantity': int(batches.quantity),
                            'status': request.form['statusTransaction']
                        }

            new_transaction_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)
            requests.post(  new_transaction_address,
                            json=json_object,
                            headers={'Content-type': 'application/json'})  

            flash('Batch has been sent to retailer', 'info')
            flash('Blockchain created', 'info')

            return redirect(url_for('home')) #redirect user to home page so that they can mine the blockchain

          

"""
Transactions
"""
@app.route('/user_transactions') #transactions log made
@login_required
def user_transactions():
    fetch_transactions()
    users = User.query.filter_by(role = "Retailer").all() #get all user id that is distributor

    return render_template('user_transactions.html', 
                            title = "View All Transactions", 
                            transactions = transactions,
                            users = users, 
                            node_address = CONNECTED_NODE_ADDRESS, 
                            readable_timer = timestamp_to_string)


def fetch_current_user_transactions():
    """
    Fetch the transactions of the currently connected user
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        transactions_user=[]
        data_transactions=[]
        chain = json.loads(response.content)
        # chain = response.json()
        for element in chain["chain"]:
            for transaction_elem in element["transactions"]:
                data_transactions.append(transaction_elem)

        current_transactions = sorted(data_transactions, key=lambda k: k['timestamp'], reverse=True)

        return sorted(transactions_user, key=lambda k: k['timestamp'], reverse=True)

@app.route('/submit_accept_transaction', methods=['POST'])
@login_required
def submit_accept_transaction():
    """
    Endpoint to the confirmation of a transaction in the blockchain
    """
    if request.method == 'POST':
        json_object = {
            'batch_id': int(request.form['batch_id']),
            'sender_id': int(request.form['sender_id']),
            'recipient_id': int(current_user.id),
            'quantity': int(request.form['quantity']),
            'status': request.form['statusTransaction']
        }

        #Submit a transaction 
        submit_accept_transaction = "{}/response_transaction".format(CONNECTED_NODE_ADDRESS)

        requests.post(submit_accept_transaction,
                      json=json_object,
                      headers={'Content-type': 'application/json'})

        #mine_blockchain()

        return redirect(url_for('user_transactions'))


def fetch_transactions():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]: # refers to /chain route (chain_data)
            for transaction in block["transactions"]:
                transaction["index"] = block["index"]
                transaction["hash"] = block["previous_hash"]
                content.append(transaction)

        # store_transaction = collection.insert_one(chain) #- store into mongodb
        global transactions
        transactions = sorted(content, key=lambda k: k['timestamp'],
                        reverse=True)
    
    if response.status_code == 404:
        flash("Error 404 not found", "error")


#Url to return to home page 
@app.route("/")
def home():
    fetch_transactions()

    return render_template('index.html', 
                            title = "View All Transactions", 
                            transactions = transactions, 
                            node_address = CONNECTED_NODE_ADDRESS, 
                            readable_timer = timestamp_to_string)


"""
Additional Function
"""
def timestamp_to_string(epoch_time):
    """
    Convert the timestamp to a readable string
    """
    return dt.datetime.fromtimestamp(epoch_time).strftime('%d/%m/%Y - %H:%M:%S')

#from json file store into database
@app.route('/store_mongodb', methods=['POST', 'GET'])
def store_mongo():
    #open the blockchain.json file that was stored
    with open('blockchain.json') as file: 
        file_data = json.load(file)

    #if more than one json entry use insert_many instead of insert_one
    if isinstance(file_data, list):
        collection.insert_many(file_data)
    else:
        collection.insert_one(file_data)

    response = {'message': 'Blockchain has been stored into the database'}
    return jsonify(response), 200

