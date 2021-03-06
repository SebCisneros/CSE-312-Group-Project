
from email.mime import multipart
import socketserver

# stderr & stdout
import sys

# To get file paths
import os

import json
import random

from backend.router import Router
from backend.auth import Auth
from backend.posts import Posts
import backend.database as db
from backend.websocket_parser import WSFrame
import backend.websocket_helper as ws

from pymongo import MongoClient
client = MongoClient("mongodb://mongo:27017/newdock")

usersDB = client['users']

userAccountCollection = usersDB["user_accounts"]


class request_handler(socketserver.BaseRequestHandler):
    # List of codes that send content to the client
    content_codes = [b"200 OK", b"201 Created", b"404 Not Found"]
    post_count = 0
    key = ''    # for websocket
    user = ''   # username from the parsed cookie
    websocket_connections = []  # stores username & the class request_handler

    def create_response(self, http_version, response_code, content_type, content, redirect, encoded_hash, cookies):
        response = http_version + b" "
        response += response_code + b"\r\n"
        if cookies is not None:
            print(cookies)
            sys.stdout.flush()
            sys.stderr.flush()
            if "username" in cookies:
                print(cookies["username"])
                response += b"Set-Cookie: username=" + bytes(cookies["username"], "UTF-8") + b"\r\n"
            if "email" in cookies:
                print(cookies["email"])
                response += b"Set-Cookie: email=" + bytes(cookies["email"], "UTF-8") + b"\r\n"
            if "xsrf_token" in cookies:
                print(cookies["xsrf_token"])
                response += b"Set-Cookie: xsrf_token=" + bytes(cookies["xsrf_token"], "UTF-8") + b"; Max-Age=3600\r\n"
            if "auth_token" in cookies:
                print(cookies["auth_token"])
                response += b"Set-Cookie: auth_token=" + bytes(cookies["auth_token"], "UTF-8") + b"; Max-Age=3600; HttpOnly\r\n"
        if response_code in self.content_codes:
            response += b"Content-Type: " + content_type + b"\r\n" + b"charset:UTF-8\r\n"
            if content_type == b"image/jpeg":
                response += b"X-Content-Type-Options: nosniff\r\n"
            response += b"Content-Length: " + bytes(str(len(content)), "UTF-8") + b"\r\n\r\n"
            response += content
        else:
            if response_code == b"301 Moved Permanently":
                response += b"Location: " + redirect + b"\r\n"
            if response_code == b"101 Switching Protocols":
                response += b"Upgrade: websocket\r\n"
                response += b"Connection: Upgrade\r\n"
                response += b"Sec-WebSocket-Accept: " + encoded_hash + b"\r\n\r\n"
                # print("Where will the control return????")
                # print()
            if response_code != b"101 Switching Protocols":
                response += b"Content-Length: 0\r\n"
        self.request.sendall(response)

    def interpret_GET(self, request):
        if routing.validate_route(request):
            redirect = routing.get_redirect(request)
            if redirect is not None:
                # redirect to new page
                self.create_response(b"HTTP/1.1", b"301 Moved Permanently", None, None, bytes(redirect, "UTF-8"), None, None)
            # websocket handshake
            elif request == '/websocket':
                # print("working on handshake response\n")
                key = request_handler.key
                hashed_key = ws.compute_accept(key).encode()
                # print("Hashed key: ")
                # print(hashed_key)
                # print()
                self.create_response(b"HTTP/1.1", b"101 Switching Protocols", b"NA", b"", None, hashed_key, None)
                # print("Buffering and WS parsing starts here.")
                # parse, control returns here
                # here, just validated
                # get the user name from the page cookies

                username = request_handler.user
                handler = self

                request_handler.websocket_connections.append({'username': username, 'socket': handler})

                while True:
                    ws_frame_raw = self.request.recv(1024)
                    print(ws_frame_raw)
                    ws_frame = WSFrame(ws_frame_raw)
                    if ws_frame.opcode == 8:
                        print("Disconnection")
                        print(request_handler.websocket_connections)
                        to_delete = None

                        for connection in request_handler.websocket_connections:
                            if connection['socket'] == handler:
                                to_delete = connection
                        if to_delete:
                            request_handler.websocket_connections.remove(to_delete)
                        print(request_handler.websocket_connections)
                        break

                    while not ws_frame.finished_buffering:
                        more_bytes = handler.request.recv(1024)
                        ws_frame.frame_bytes = ws_frame.frame_bytes + more_bytes
                        ws_frame.check_payload()
                    ws_frame.extract_payload()
                    ws_frame.print_frame()
                    message_json = ws_frame.payload.decode()
                    message = json.loads(message_json)
                    message_type = message['messageType']

                    if message_type == 'chatMessage':
                        # {'message_type': 'chatMessage', 'comment': comment}
                        for user in request_handler.websocket_connections:
                            message_data = {'messageType': 'chatMessage', 'username': self.sanitize_input(username),
                                            'comment': self.sanitize_input(message['comment'])}
                            # for printing the chats in the html page
                            # history.append({'username': username, 'comment': message['comment']})
                            print("sending: " + str(message_data))
                            message_bytes = json.dumps(message_data).encode()
                            to_send = ws.generate_frame(message_bytes)
                            user['socket'].request.sendall(to_send)
                    else:
                        print("Invalid WS messageType")


            else:
                self.create_response(b"HTTP/1.1", b"200 OK", bytes(routing.get_content_type(request), "UTF-8"), routing.get_content(request), None, None, None)
        else:
            # page not found
            self.create_response(b"HTTP/1.1", b"404 Not Found", b"text/plain", b"404: Content not found.", None, None, None)

    def interpret_PUT(self, content, user_id):
        record = json.loads(content)
        # set response equal to DB modification function
        response = None
        if response is None:
            self.create_response(b"HTTP/1.1", b"404 Not Found", b"text/plain", b"404: Content not found.", None, None, None)

    def interpret_DELETE(self, user_id):
        self.create_response(b"HTTP/1.1", b"404 Not Found", b"text/plain", b"404: Content not found.", None, None, None)

    def get_headers(self, received_data):
        decoded_data = received_data.split(b'\r\n\r\n', 1)
        content = decoded_data[1]
        data_types = decoded_data[0].decode().split(' ', 2)
        request_method = data_types[0]
        request_uri = data_types[1]
        http_content = data_types[2].split('\r\n', 1)
        http_version = http_content[0]
        header_array = http_content[1].split('\r\n')
        header_dict = {}
        for value in header_array:
            value_array = value.split(":", 1)
            header_dict[value_array[0]] = str.lstrip(value_array[1])
        if "Content-Length" in header_dict:
            if int(header_dict["Content-Length"]) + len(received_data) > 2048:
                packet_size = 2048
                while packet_size < int(header_dict["Content-Length"]):
                    content = content + self.request.recv(2048)
                    packet_size += 2048

        if "Content-Type" in header_dict:
            if "text" in header_dict["Content-Type"]:
                content = content.decode()

        cookieDict = {}
        if "Cookie" in header_dict:
            cookieData = header_dict["Cookie"]
            cookieData = cookieData.split("; ")
            for data in cookieData:
                data = data.split("=")
                cookieDict[data[0]] = data[1]

        match request_method:
            case "GET":
                # getting "'Sec-WebSocket-Key" for websocket
                if request_uri == "/websocket":
                    # print("Storing Sec-WebSocket-Key....")
                    request_handler.key = header_dict["Sec-WebSocket-Key"]
                    if 'username' in cookieDict:
                        request_handler.user = cookieDict['username']
                    # print("Stored...")

                self.get_posts_from_database()
                routing.edit_html()
                self.interpret_GET(request_uri)
                # print("Parsing in the get_headers")

            case "POST":
                if "Content-Type" in header_dict and "multipart/form-data" in header_dict["Content-Type"]:
                    data_dict = {}
                    boundary = header_dict["Content-Type"].split("boundary=", 1)
                    form_data = content.split(bytes(("--" + boundary[1]), "UTF-8"))
                    for i in form_data:
                        if (i != b"") and (i != b"--\r\n"):
                            decoded_boundary = i.split(b'\r\n\r\n', 1)
                            boundary_header_array = decoded_boundary[0].decode().split('\r\n')
                            boundary_header_dict = self.createBoundaryHeaderDict(boundary_header_array)
                            if "Content-Disposition" in boundary_header_dict:
                                disposition_info_array = boundary_header_dict["Content-Disposition"].split("; ")
                                disposition_info_dict = self.createDispositionInfoDict(disposition_info_array)

                                if "name" in disposition_info_dict:
                                    match disposition_info_dict["name"]:
                                        case "email" | "username" | "password" | "passwordConfirmation" | "comment":
                                            parsed_data = self.sanitize_input(decoded_boundary[1].decode()).rstrip()

                                            # something = userAccountCollection.insert_one({'x': 1})

                                            data_dict[disposition_info_dict["name"]] = parsed_data
                                        case "upload":
                                            image_data = decoded_boundary[1]
                                            data_dict[disposition_info_dict["name"]] = image_data
                                        case "xsrf_token":
                                            token_data = decoded_boundary[1].decode()[:-2]
                                            data_dict[disposition_info_dict["name"]] = token_data

                    print(data_dict)

                    # Do stuff to data dic
                    self.multipartDataProcessing(data_dict, request_uri, cookieDict)

            case "PUT":
                self.create_response(b"HTTP/1.1", b"404 Not Found", b"text/plain", b"404: Content not found.", None, None, None)

            case "DELETE":
                self.create_response(b"HTTP/1.1", b"404 Not Found", b"text/plain", b"404: Content not found.", None, None, None)

    def handle(self):
        received_data = self.request.recv(2048)
        if len(received_data) == 0:
            return
        client_id = self.client_address[0] + ":" + str(self.client_address[1])
        self.get_headers(received_data)

    def createBoundaryHeaderDict(self, boundary_header_array):
        boundary_header_dict = {}
        for boundary_value in boundary_header_array:
            boundary_value_array = boundary_value.split(":", 1)
            if len(boundary_value_array) > 1:
                boundary_header_dict[boundary_value_array[0]] = str.lstrip(
                    boundary_value_array[1])
        return boundary_header_dict

    def createDispositionInfoDict(self, disposition_info_array):
        disposition_info_dict = {}
        for disposition_value in disposition_info_array:
            disposition_value_array = disposition_value.split("=", 1)
            if len(disposition_value_array) > 1:
                disposition_info_dict[disposition_value_array[0]] = disposition_value_array[
                    1].strip('"')
        return disposition_info_dict

    def multipartDataProcessing(self, form_data_dictionary, request_uri, cookie_dict):
        # If user is registering
        print(request_uri)
        sys.stdout.flush()
        sys.stderr.flush()
        match request_uri:
            case "/registration":
                self.register_user(form_data_dictionary)
            case "/login":
                self.login_user(form_data_dictionary)
            case "/image-upload":
                print(form_data_dictionary["xsrf_token"])
                sys.stdout.flush()
                sys.stderr.flush()
                if ("xsrf_token" in form_data_dictionary) and ("email" in cookie_dict):
                    if authentication.verify_token(form_data_dictionary["xsrf_token"], cookie_dict["email"]):
                        self.create_post(form_data_dictionary, cookie_dict)
                    else:
                        self.create_response(b"HTTP/1.1", b"403 Forbidden", b"text/plain", b"403: Forbidden.", None, None, None)
                else:
                    self.create_response(b"HTTP/1.1", b"301 Moved Permanently", None, None, b"/", None, None)

    def create_post(self, data_dictionary, cookie_dict):
        if ("upload" in data_dictionary) and ("comment" in data_dictionary) and ("username" in cookie_dict):
            save_path = './posts'
            file_name = "post-" + str(random.randrange(0, 100000000)) + "-image"
            full_name = os.path.join(save_path, file_name)
            with open(full_name, "wb") as image_file:
                image_file.write(data_dictionary["upload"])
            posting.add_post(cookie_dict["username"], data_dictionary["comment"], full_name, file_name)
            self.create_response(b"HTTP/1.1", b"301 Moved Permanently", None, None, b"/posts", None, None)
        else:
            self.create_response(b"HTTP/1.1", b"301 Moved Permanently", None, None, b"/upload", None, None)

    def get_posts_from_database(self):
        posts_list = posting.get_all_posts()
        if posts_list is not None:
            routing.flush_posts()
            for post in posts_list:
                if ("image_name" in post) and ("image_path" in post) and ("username" in post):
                    routing.create_route("/posts/" + post["image_name"], None, "image/jpeg", post["image_path"])
                    routing.add_post(post["title"], post["username"], post["image_path"])
            routing.edit_html()
            routing.create_route("/posts", None, "text/html", (root + r"/posts.html"))

    def register_user(self, dataDic):
        if ("email" in dataDic) and ("username" in dataDic) and ("password" in dataDic):
            if dataDic["password"] == dataDic["passwordConfirmation"]:

                newUserEntry = {
                    "email": dataDic["email"],
                    "username": dataDic["username"],
                    "password": dataDic["password"]
                }
                # db.create(newUserEntry)
                userAccountCollection.insert_one(newUserEntry)

                auth_token = authentication.add_user(newUserEntry["email"], newUserEntry["password"])
                xsrf_token = authentication.create_token(dataDic["email"])
                print("Added " + dataDic["email"] + "to authentication database. \n Auth token is " + auth_token + "\n xsrf token is " + xsrf_token)
                sys.stdout.flush()
                sys.stderr.flush()

                self.create_response(b"HTTP/1.1", b"301 Moved Permanently", None, None, b"/posts", None, {"auth_token": auth_token, "xsrf_token": xsrf_token, "username": dataDic["username"], "email": dataDic["email"]})
            else:
                self.create_response(b"HTTP/1.1", b"301 Moved Permanently", None, None, b"/registration", None, None)
        else:
            self.create_response(b"HTTP/1.1", b"301 Moved Permanently", None, None, b"/registration", None, None)

    def login_user(self, data_dictionary):
        if ("email" in data_dictionary) and ("password" in data_dictionary):
            auth_token = authentication.login_user(data_dictionary["email"], data_dictionary["password"])
            xsrf_token = authentication.create_token(data_dictionary["email"])
            if auth_token is not None:
                userAccount = userAccountCollection.find_one({"email":data_dictionary["email"]})
                username = userAccount["username"]
                self.create_response(b"HTTP/1.1", b"301 Moved Permanently", None, None, b"/posts", None, {"auth_token": auth_token, "xsrf_token": xsrf_token, "username": username})
            else:
                self.create_response(b"HTTP/1.1", b"301 Moved Permanently", None, None, b"/login", None, None)
        else:
            self.create_response(b"HTTP/1.1", b"301 Moved Permanently", None, None, b"/login", None, None)

    def sanitize_input(self, user_input):
        user_input1 = user_input.replace('&', '&amp;')
        user_input2 = user_input1.replace('<', '&lt')
        user_input3 = user_input2.replace('>', '&gt')
        return user_input3


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8080
    print("Initializing server on port" + str(port) + ".\n\n\n\n\n")
    sys.stdout.flush()
    sys.stderr.flush()

    # Initialize routing and authentication
    routing = Router()
    authentication = Auth()
    posting = Posts()
    # Generate static routes
    root = os.path.realpath(os.path.join(os.path.dirname(__file__), ''))
    routing.create_route("/", None, "text/html", (root + r"/index.html"))
    routing.create_route("/upload", None, "text/html", (root + r"/upload.html"))
    routing.create_route("/posts", None, "text/html", (root + r"/posts.html"))
    routing.create_route("/chat", None, "text/html", (root + r"/chat.html"))
    routing.create_route("/chat.js", None, "text/javascript", (root + r"/chat.js"))
    routing.create_route("/websocket", None, "NA", b'')

    png_names = ["ribbit_logo"]
    for image in png_names:
        routing.create_route("/frontend/images/" + image + ".png", None, "image/png", (root + r"/frontend/images/" + image + ".png"))
    jpg_names = ["wednesday"]
    for image in jpg_names:
        routing.create_route("/frontend/images/" + image + ".jpg", None, "image/jpeg", (root + r"/frontend/images/" + image + ".jpg"))
    css_names = ["main", "login"]
    for stylesheet in css_names:
        routing.create_route("/frontend/styles/" + stylesheet + ".css", None, "text/css", (root + r"/frontend/styles/" + stylesheet + ".css"))
    routing.create_route("/login", None, "text/html", (root + r"/login.html"))
    routing.create_route("/registration", None, "text/html", (root + r"/registration.html"))
    routing.create_route("/main.css", None, "text/css", (root + r"/main.css"))
    routing.create_route("/functions.js", None, "text/javascript", (root + r"/functions.js"))

    with socketserver.ThreadingTCPServer((host, port), request_handler) as server:
        server.serve_forever()
