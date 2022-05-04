import json
import sys

import database as db


# TODO: Test the API in Docker to see if it works.
def parse_user_id(request_path: str):
    """
        Parses the request path to find the user_id and puts it in {'id': #} dictionary format

        :param request_path: path from the request
        :return: Dictionary with `id` as key and int _id as value
    """
    path_split = request_path.split('/')
    _id = int(path_split[2])
    id_dict = {'id': _id}
    return id_dict


def create(content: bytes):
    """Creates the collection calling db.create() using the body of Request and sends '201 created response code"""

    body_dict = json.loads(content.decode())
    body_dict['id'] = db.get_next_id()

    db.create(body_dict)
    print("Record created")
    return body_dict


def list_all():
    """returns all the users and their information stored in the database"""

    response = db.list_all()
    return response


def retrieve(request_uri: str):
    """
        Retrieves the information about a specific id.

        :param request_uri: HTTP request path
        :return None if the user doesn't exist, the user information if the user exists
    """

    # is the id going to be parsed and provided for list_all
    id = parse_user_id(request_uri)
    response_body = db.retrieve_single(id)
    if response_body is not None:
        print("User doesn't exist")
        return response_body
    else:
        print("User found...")
        return response_body


def update(content: bytes, request_uri: str):
    """
        Takes the content in byte format and request path and updates by finding the user from path with the content
        provided

        :param content: raw bytes from the request body
        :param request_uri: http request path
        :return None if the user doesn't exist otherwise just prints if it's updated
    """

    id = parse_user_id(request_uri)
    update_info = json.loads(content.decode())
    print(update_info)
    print(type(update_info))
    exists = db.retrieve_single(id)
    if exists is None:
        print("Couldn't find the user.")
        return exists
    else:
        db.update(id, update_info)
        print("Information updated...")


def delete(request_uri: str):
    """Deletes the information of an id if it exists"""

    id = parse_user_id(request_uri)
    exists = db.retrieve_single(id)
    if exists is None:
        print("User doesn't exists")
        return exists
    else:
        db.delete(id)
        print("User deleted...")
