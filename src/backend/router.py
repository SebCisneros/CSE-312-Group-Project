import os


from pymongo import MongoClient
client = MongoClient("mongodb://mongo:27017/newdock")

usersDB = client['users']

userAccountCollection = usersDB["user_accounts"]

class Router:
    # Keeps track of where routes redirect to (if applicable)
    redirect_dict = {}
    # Keeps track of content types for each route
    content_type_dict = {}
    # Stores text/plain and text/json data as strings, other files as paths so they can be read
    content_dict = {}
    titles = [" "]
    usernames = [" "]
    images = [" "]
    likes = [" "]
    html = b""

    # Add route to dictionaries
    # format is (browser path, path to redirect to, http content type, file / text)
    def create_route(self, path, redirect, content_type, content):
        self.redirect_dict[path] = redirect
        self.content_type_dict[path] = content_type
        self.content_dict[path] = content

    # Deletes a route from the dictionaries
    def delete_route(self, path):
        del self.redirect_dict[path]
        del self.content_dict[path]
        del self.content_type_dict[path]

    # Returns the content type as a string
    def get_content_type(self, path):
        return self.content_type_dict[path]

    # Returns the content as bytes
    def get_content(self, path):
        if path == "/posts":
            return self.html
        elif (self.content_type_dict[path] != "text/plain") and (self.content_type_dict[path] != "text/json"):
            content = self.read_file(self.content_dict[path])
        else:
            content = bytes(self.content_dict[path], "UTF-8")
        return content

    # Check if route exists
    def validate_route(self, path):
        if path in self.redirect_dict.keys():
            return True
        False

    # Check if path redirects
    def get_redirect(self, path):
        return self.redirect_dict[path]

    # Reads a file and returns it in the form of bytes
    def read_file(self, filename):
        with open(filename, "rb") as file:
            encoded_file = file.read()
            file.close()
        return encoded_file

    # Add post to list of posts
    def add_post(self, title, username, image):
        self.titles.append(title)
        self.usernames.append(username)
        self.images.append(image)

    # Wipe posts lists clean
    def flush_posts(self):
        self.titles = [" "]
        self.usernames = [" "]
        self.images = [" "]




    def addUserChat(self, file ,users):
        new_file = file + b'<h2> Chat: </h2>'

        for user in users:
            userName = user["username"]
            new_file = new_file + b'<br/>\r\n'
            new_file = new_file + b'<form action="/sendMessage/'+ bytes(userName, "UTF-8") + b'" id="'+ bytes(userName, "UTF-8") + b'-message-form" method="post" enctype="multipart/form-data">\r\n'
            new_file = new_file + b'<input value="form_xsrf" name="xsrf_token" hidden>\r\n'
            new_file = new_file + b'<label for="login-form-' + bytes(userName, "UTF-8") + b'"> ' + bytes(userName, "UTF-8") + b': </label>\r\n'
            new_file = new_file + b'<input type="text" id="login-form-'+ bytes(userName, "UTF-8") + b'" name="message"><br><br>\r\n'
            new_file = new_file + b'<input type="submit" value="Send">\r\n'
            new_file = new_file + b'</form>\r\n'
        return new_file

    def edit_html(self):
        original_html = self.read_file(self.content_dict["/posts"])

        users = userAccountCollection.find({}, {"_id":0})

        if len(self.titles) == 0 and len(self.usernames) == 0 and len(self.images) == 0:
            new_html = original_html
            new_html = new_html.split(b"{{CONTENT}}", 1)
            end_file = new_html[1]
            new_file = new_html[0]

            if (users != None) or (len(users) != 0):
                new_file = self.addUserChat(new_file, users)  

            new_file = new_file + end_file
            self.html = new_file

        else:
            new_html = original_html
            new_html = new_html.split(b"{{CONTENT}}", 1)
            end_file = new_html[1]
            new_file = new_html[0]
            if len(self.titles) > 1:
                for i in range(0, len(self.titles)):
                    if self.titles[i] != " ":
                        new_file = new_file + b'<br/>\r\n'
                        new_file = new_file + b'<div class="post">\r\n'
                        new_file = new_file + b'<h1 class="post-title">' + bytes(self.titles[i], "UTF-8") + b'</h1>\r\n'
                        new_file = new_file + b'<p class="post-username">by ' + bytes(self.usernames[i], "UTF-8") + b'</p>\r\n'
                        new_file = new_file + b'<img class="post-image" src="' + bytes(self.images[i], "UTF-8") + b'">\r\n'
                        new_file = new_file + b'</div>\r\n'

            if (users != None) or (len(users) != 0):
                new_file = self.addUserChat(new_file, users)  

            new_file = new_file + end_file
            self.html = new_file
