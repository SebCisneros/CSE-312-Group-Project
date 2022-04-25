import json
import sys

# import util.database as db
# from util.response import generate_response
# from util.router import Route
# from util.request import Request
#
#
# def add_paths(router):
#     router.add_route(Route('POST', '/users', create))
#     router.add_route(Route('GET', '/users/.', retrieve))
#     router.add_route(Route('GET', '/users', list_all))
#     router.add_route(Route('PUT', '/users/.', update))
#     router.add_route(Route('DELETE', '/users/.', delete))


def parse_user_id(request):
    """
    Parses the request to find the user_id
    :param request: path from the request
    :return: Dictionary with `id` as key and int _id as value
    """
    path_split = request.path.split('/')
    _id = int(path_split[2])
    id_dict = {'id': _id}
    return id_dict


def create(request, handler):
    """Creates the collection calling db.create() using the body of Request and sends '201 created response code"""

    body_string = request.body.decode()
    body_dict = json.loads(body_string)
    body_dict['id'] = db.get_next_id()

    db.create(body_dict)

    response = generate_response(json.dumps(body_dict).encode(), 'application/json', '201 Created')
    handler.request.sendall(response)


# To-Do: add retrieve, list_all, update, delete methods in this file
def list_all(request, handler):
    """Shows all the contents of the collection calling db.list_all() function"""

    response = generate_response(json.dumps(db.list_all()).encode(), 'application/json', '200 Ok')
    handler.request.sendall(response)


def retrieve(request, handler):
    """Retrieves the information about a specific id."""

    id = parse_user_id(request)
    print(id)

    response_body = db.retrieve_single(id)
    print(response_body)
    if response_body is not None:
        response = generate_response(json.dumps(response_body).encode(), 'application/json', '200 Ok')
        handler.request.sendall(response)
    else:
        response = generate_response('Not Found'.encode(), 'text/plain; charset=utf-8', '404 Not Found')
        handler.request.sendall(response)


def update(request, handler):
    """Checks if the id exists or not based on that updates the id with body retrieved from Request(in dictionary format)
        and sends appropriate response."""

    id = parse_user_id(request)
    update_info = json.loads(request.body.decode())
    print(update_info)
    print(type(update_info))
    exists = db.retrieve_single(id)
    if exists is None:
        response = generate_response('Not Found'.encode(), 'text/plain; charset=utf-8', '404 Not Found')
        handler.request.sendall(response)
    else:
        db.update(id, update_info)
        response = response = generate_response('update done'.encode(), 'text/plain; charset=utf-8', '200 Ok')
        handler.request.sendall(response)


def delete(request, handler):
    """Deletes the information of an id if it exists"""
    id = parse_user_id(request)
    exists = db.retrieve_single(id)
    if exists is None:
        response = generate_response('Not Found'.encode(), 'text/plain; charset=utf-8', '404 Not Found')
        handler.request.sendall(response)
    else:
        db.delete(id)
        response = response = generate_response(b'', 'text/plain; charset=utf-8', '204 No Content')
        handler.request.sendall(response)






