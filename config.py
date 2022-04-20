"""
Configure a database named app.db in the main directory of the application
"""
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #SECRET_KEY = os.environ.get('SECRET_KEY') or 'this-is-not-secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False #does not send a single every time database make a change

"""
MongoDB Credentials 
"""

# import pymongo
# from pymongo import MongoClient

# cluster = MongoClient("mongodb+srv://TanZY1310:<SydRFw3iofRoGmrr>@fypproject.7b0sh.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
