import json
import sys
from pymongo import MongoClient

mongo_client = MongoClient('mongo')
db = mongo_client['cse312']

users_collection = db['users']
users_id_collection = db['users_id']


def get_next_id():
    """Creates custom id values"""
    id_object = users_id_collection.find_one({})
    if id_object:
        next_id = int(id_object['last_id']) + 1
        users_id_collection.update_one({}, {'$set': {'last_id': next_id}})
        return next_id
    else:
        users_id_collection.insert_one({'last_id': 1})
        return 1


def create(user_data: dict):
    """Creates record in the database."""

    users_collection.insert_one(user_data)
    user_data.pop('_id')


def list_all():
    """Returns all the records in the database in  `dict` format."""

    all_users = users_collection.find({}, {'_id': 0})
    return list(all_users)


def retrieve_data_by_username(user: str):
    """
    Retrieves the information based on the username.

    :param user: username in `str` format
    :return: all user information in `dict inside a list format` example: [{}] or `None` if the user doesn't exist.
    """

    user_name = {'username': user}
    data = []
    for i in users_collection.find(user_name):
        data.append(i)
    if len(data) > 0:
        data[0].pop('_id')
        return data
    else:
        return None


def update_by_username(user_find: str, user_update: dict):
    """
    Updates the information based on the username.

    :param user_find: username in `str` format
    :param user_update: information to update in `dictionary` key-value pair format.
    :return: None if the user doesn't exist.
    """
    user_to_update = {'username': user_find}
    user_data = retrieve_data_by_username(user_to_update)
    if user_data is None:
        return None
    users_collection.update_one(user_to_update, {'$set': user_update})
    print("Data updated successfully...")


def delete_by_username(user: str):
    """
    Deletes the user information if the user exists.

    :param user: username in `str` format.
    :return: None if the user doesn't exist.
    """
    username = {'username': user}

    user_data = retrieve_data_by_username(username)
    if user_data is None:
        return None
    users_collection.delete_one(username)
    print("User deleted successfully...")

