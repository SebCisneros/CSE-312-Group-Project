
import socketserver

# stderr & stdout
import sys

# To get file paths
import os

import json


from backend.router import Router


class request_handler(socketserver.BaseRequestHandler):
    # List of codes that send content to the client
    content_codes = [b"200 OK", b"201 Created", b"404 Not Found"]

    def create_response(self, http_version, response_code, content_type, content, redirect, encoded_hash):
        response = http_version + b" "
        response += response_code + b"\r\n"
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
            if response_code != b"101 Switching Protocols":
                response += b"Content-Length: 0\r\n"
        self.request.sendall(response)

    def interpret_GET(self, request):
        if routing.validate_route(request):
            redirect = routing.get_redirect(request)
            if redirect is not None:
                # redirect to new page
                self.create_response(b"HTTP/1.1", b"301 Moved Permanently", None, None, bytes(redirect, "UTF-8"), None)
            else:
                self.create_response(b"HTTP/1.1", b"200 OK", bytes(routing.get_content_type(request), "UTF-8"), routing.get_content(request), None, None)
        else:
            # page not found
            self.create_response(b"HTTP/1.1", b"404 Not Found", b"text/plain", b"404: Content not found.", None, None)

    def interpret_POST(self, content):
        #parse content dictionary here
        record = content
        # set response equal to DB modification function
        response = None
        # Update routes
        self.create_response(b"HTTP/1.1", b"201 Created", b"text/json", bytes(json.dumps(response), "UTF-8"), None, None)

    def interpret_PUT(self, content, user_id):
        record = json.loads(content)
        # set response equal to DB modification function
        response = None
        if response is None:
            self.create_response(b"HTTP/1.1", b"404 Not Found", b"text/plain", b"404: Content not found.", None, None)

    def interpret_DELETE(self, user_id):
        self.create_response(b"HTTP/1.1", b"404 Not Found", b"text/plain", b"404: Content not found.", None, None)

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
                # print(content)
                sys.stdout.flush()
                sys.stderr.flush()
            else:
                # print(len(received_data))
                print(received_data)
                # print(received_data.decode())
                print(content)
                sys.stdout.flush()
                sys.stderr.flush()

        if "Content-Type" in header_dict:
            if "text" in header_dict["Content-Type"]:
                content = content.decode()

        match request_method:
            case "GET":
                self.interpret_GET(request_uri)

            case "POST":
                if "Content-Type" in header_dict:
                    if "multipart/form-data" in header_dict["Content-Type"]:
                        data_dict = {}
                        boundary = header_dict["Content-Type"].split("boundary=", 1)
                        print("boundary=" + boundary[1])
                        form_data = content.split(bytes(("--" + boundary[1]), "UTF-8"))
                        for i in form_data:
                            if (i != b"") and (i != b"--\r\n"):
                                # print("boundary data:  " + i.decode())
                                decoded_boundary = i.split(b'\r\n\r\n', 1)
                                boundary_header_array = decoded_boundary[0].decode().split('\r\n')
                                boundary_header_dict = {}
                                for boundary_value in boundary_header_array:
                                    boundary_value_array = boundary_value.split(":", 1)
                                    if len(boundary_value_array) > 1:
                                        boundary_header_dict[boundary_value_array[0]] = str.lstrip(
                                            boundary_value_array[1])
                                if "Content-Disposition" in boundary_header_dict:
                                    disposition_info_array = boundary_header_dict["Content-Disposition"].split("; ")
                                    disposition_info_dict = {}
                                    for disposition_value in disposition_info_array:
                                        disposition_value_array = disposition_value.split("=", 1)
                                        if len(disposition_value_array) > 1:
                                            disposition_info_dict[disposition_value_array[0]] = disposition_value_array[
                                                1].strip('"')
                                    if "name" in disposition_info_dict:
                                        if disposition_info_dict["name"] == "email":
                                            parsed_email = self.sanitize_input(decoded_boundary[1].decode())
                                            print("email: " + parsed_email)
                                            data_dict["email"] = parsed_email
                                            sys.stdout.flush()
                                            sys.stderr.flush()
                                        if disposition_info_dict["name"] == "username":
                                            parsed_username = self.sanitize_input(decoded_boundary[1].decode())
                                            print("username: " + parsed_username)
                                            data_dict["username"] = parsed_username
                                            sys.stdout.flush()
                                            sys.stderr.flush()
                                        if disposition_info_dict["name"] == "password":
                                            parsed_password = self.sanitize_input(decoded_boundary[1].decode())
                                            print("password: " + parsed_password)
                                            data_dict["password"] = parsed_password
                                            sys.stdout.flush()
                                            sys.stderr.flush()
                        self.interpret_POST(data_dict)


            case "PUT":
                self.create_response(b"HTTP/1.1", b"404 Not Found", b"text/plain", b"404: Content not found.", None, None)

            case "DELETE":
                self.create_response(b"HTTP/1.1", b"404 Not Found", b"text/plain", b"404: Content not found.", None, None)

    def handle(self):
        received_data = self.request.recv(2048)
        print(received_data)
        sys.stdout.flush()
        sys.stderr.flush()
        if len(received_data) == 0:
            return
        client_id = self.client_address[0] + ":" + str(self.client_address[1])
        print(client_id)
        self.get_headers(received_data)

    def sanitize_input(self, user_input):
        user_input1 = user_input.replace('&', '&amp;')
        user_input2 = user_input1.replace('<', '&lt')
        user_input3 = user_input2.replace('>', '&gt')
        return user_input3


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8080
    sys.stdout.flush()
    sys.stderr.flush()
    routing = Router()

    # Initialize routes
    root = os.path.realpath(os.path.join(os.path.dirname(__file__), ''))
    routing.create_route("/", None, "text/html", (root + r"/index.html"))
    routing.create_route("/login", None, "text/html", (root + r"/frontend/pages/login.html"))
    routing.create_route("/registration", None, "text/html", (root + r"/frontend/pages/registration.html"))
    routing.create_route("/style.css", None, "text/css", (root + r"/style.css"))
    routing.create_route("/functions.js", None, "text/javascript", (root + r"/functions.js"))

    with socketserver.ThreadingTCPServer((host, port), request_handler) as server:
        server.serve_forever()
