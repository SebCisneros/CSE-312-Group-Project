import hashlib

from pymongo import MongoClient

import secrets


class Auth:
    client = MongoClient("mongo")
    db = client["records"]
    users = db["user_records"]
    salt = "GeNeRaL_kEn0bI;YoV-aRe=A+bOId`oN3"

    # Adds a user to the authentication database, returns an authentication token associated with that user
    def add_user(self, email, password):
        hashed_password = hashlib.sha256((password + self.salt).encode()).digest()
        self.users.insert_one({"email": email, "password": hashed_password})
        return self.create_token(email)

    # Checks authentication database for the user's email and corresponding hashed (& salted) password
    # Returns an authentication token if it is a valid login, returns None otherwise
    def login_user(self, email, password):
        hashed_password = hashlib.sha256((password + self.salt).encode()).digest()
        user_record = list(self.users.find({"$and": [{"email": email}, {"password": hashed_password}]}))
        if len(user_record) != 0:
            return self.create_token(email)
        return None

    # Generates a randomized hex token, hashes it, and stores it on a per-user basis
    def create_token(self, email):
        token = secrets.token_hex(16)
        hashed_token = hashlib.sha256(token.encode()).digest()
        self.users.insert_one({"token": hashed_token, "email": email})
        return token

    # Takes a non-hashed token and email as input.
    # Hashes the token and if there is an email entry corresponding to the hashed token, returns True.
    # Otherwise, returns False
    def verify_token(self, token, email):
        hashed_token = hashlib.sha256(token.encode()).digest()
        user_record = list(self.users.find({"$and": [{"token": hashed_token}, {"email": email}]}))
        if len(user_record) != 0:
            return True
        return False
