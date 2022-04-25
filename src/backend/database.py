import json
import sys
from pymongo import MongoClient

mongo_client = MongoClient()
db = mongo_client['cse312']

users_collection = db['users']
users_id_collection = db['users_id']


def get_next_id():
    """Creates a custom id values"""
    id_object = users_id_collection.find_one({})
    if id_object:
        next_id = int(id_object['last_id']) + 1
        users_id_collection.update_one({}, {'$set': {'last_id': next_id}})
        return next_id
    else:
        users_id_collection.insert_one({'last_id': 1})
        return 1


def create(user: dict):
    users_collection.insert_one(user)
    user.pop('_id')


def list_all():
    all_users = users_collection.find({}, {'_id': 0})
    return list(all_users)


# takes a single key value pair and find relevant informations and put them in a list
def retrieve_single(user: dict):
    data = []
    for i in users_collection.find(user):
        data.append(i)
    if len(data) > 0:
        data[0].pop('_id')
        return data
    else:
        return None


def update(user_find: dict, user_update: dict):
    users_collection.update_one(user_find, {'$set': user_update})


def delete(user: dict):
    users_collection.delete_one(user)



