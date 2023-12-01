import datetime
from functools import wraps

from flask import request
from flask_jwt_extended import current_user


# decorator for returning the code execution time, monitoring cookies and IP addresses.
def monitor(function=None):
    @wraps(function)
    def wrapper(*args, **kwargs):
        s = datetime.datetime.now()
        _ = function(*args, **kwargs)
        e = datetime.datetime.now()
        print("Execution Time:{}".format(e - s))
        print("Ip Address  : {} ".format(request.remote_user))
        print("Cookies : {} ".format(request.cookies))
        print(request.user_agent)
        return _

    return wrapper

# decorator that only allow the admin user to assess the routes
def admin_required(function=None):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return {"status": 403, "message": "Admin access only is required"}, 403
        return function(*args, **kwargs)
    return wrapper

# decorator that only allow the normal user to assess the routes
def  user_required(function=None):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.is_admin:
            return {"status": 403, "message": "User access only is required"}, 403
        return function(*args, **kwargs)
    return wrapper