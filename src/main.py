
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
        record = json.loads(content)
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
        decoded_data = received_data.decode().split('\r\n\r\n', 1)
        content = decoded_data[1]
        data_types = decoded_data[0].split(' ', 2)
        request_method = data_types[0]
        request_uri = data_types[1]
        http_content = data_types[2].split('\r\n', 1)
        http_version = http_content[0]
        header_array = http_content[1].split('\r\n')
        header_dict = {}
        print(len(received_data))
        print(received_data)
        sys.stdout.flush()
        sys.stderr.flush()
        for value in header_array:
            value_array = value.split(":", 1)
            header_dict[value_array[0]] = str.lstrip(value_array[1])
        if "Content-Length" in header_dict:
            if int(header_dict["Content-Length"]) > 1024:
                packet_size = 1024
                content = content.encode()
                while packet_size < int(header_dict["Content-Length"]):
                    content = content + self.request.recv(1024)
                    packet_size += 1024
                print(content)
                sys.stdout.flush()
                sys.stderr.flush()
            else:
                print(len(received_data))
                print(received_data)
                print(received_data.decode())
                sys.stdout.flush()
                sys.stderr.flush()
        match request_method:
            case "GET":
                self.interpret_GET(request_uri)

            case "POST":
                self.interpret_POST(content)

            case "PUT":
                self.create_response(b"HTTP/1.1", b"404 Not Found", b"text/plain", b"404: Content not found.", None, None)

            case "DELETE":
                self.create_response(b"HTTP/1.1", b"404 Not Found", b"text/plain", b"404: Content not found.", None, None)

    def handle(self):
        received_data = self.request.recv(1024)
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
    routing.create_route("/style.css", None, "text/css", (root + r"/style.css"))
    routing.create_route("/functions.js", None, "text/javascript", (root + r"/functions.js"))

    with socketserver.ThreadingTCPServer((host, port), request_handler) as server:
        server.serve_forever()