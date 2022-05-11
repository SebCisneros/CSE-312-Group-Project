from pymongo import MongoClient


class Posts:
    client = MongoClient("mongo")
    db = client["records"]
    users = db["user_records"]
    post_count = 0

    # Adds a post to the database
    def add_post(self, username, title, image_path, image_name):
        self.post_count += 1
        self.users.insert_one({"post_id": self.post_count, "username": username, "title": title, "image_path": image_path, "image_name": image_name, "likes": 1})

    # Returns a list of all posts. If there are no posts, return None.
    def get_all_posts(self):
        user_record = list(self.users.find({}))
        if len(user_record) != 0:
            return user_record
        return None

    # Returns a list of all posts by a specific user. If there are no posts, return None.
    def get_all_posts_by_username(self, username):
        user_record = list(self.users.find({"username": username}))
        if len(user_record) != 0:
            return user_record
        return None

    # Returns a post with the specified id. If no post with that id exists, return None.
    def get_post_by_id(self, post_id):
        user_record = list(self.users.find({"post_id": post_id}))
        if len(user_record) != 0:
            return user_record[0]
        return None

    # Updates all posts by a specific user if their username has been changed
    def update_username(self, old_username, new_username):
        self.users.update({"username": old_username}, {"$set": {"username": new_username}})
