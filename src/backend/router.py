class Router:
    # Keeps track of which route redirects
    redirect_dict = {}
    # Keeps track of content types for each route
    content_type_dict = {}
    # Stores text/plain and text/json data as strings, other files as paths so they can be read
    content_dict = {}

    # Add route to dictionaries
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
        if (self.content_type_dict[path] != "text/plain") and (self.content_type_dict[path] != "text/json"):
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
