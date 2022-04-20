import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://TanZY1310:SydRFw3iofRoGmrr@fypproject.7b0sh.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

dbMongo = cluster["SupplyChain"]
collection = dbMongo["Transaction"]

# post = {"_id": 0, "name": "tan", "score": 5}
# post1 = {"_id": 1, "name": "joe", "score": 6}
# post2 = {"_id": 2, "name": "mama", "score": 7}

# results = collection.insert_many([post, post1, post2]) 

#results = collection.find()#similar to db query
# results = collection.delete_many({}) #delete

# results = collection.update_one({"_id": 0}, {"$set":{"name": "tim"} }) #edit #add extra field by adding new variable 

# post_count = collection.count_documents({}) #print total data/post in database 
# print(post_count)