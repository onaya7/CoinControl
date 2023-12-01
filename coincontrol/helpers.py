import requests
import os
import uuid
from flask import make_response



"""
Helper functions are stored here

"""

def get_google_provider_cfg():
    try:
        response = requests.get(os.environ.get("GOOGLE_DISCOVERY_URL")).json()
    except Exception as e:
        return e
    return response


def generate_uuid() -> str:
    return str(uuid.uuid4())


# function to set access cookie
def set_access_cookie(response: make_response, token, duration=3600) -> make_response:
    cookie = dict()
    
    cookie["key"] = "access_token"
    cookie["value"] = token
    cookie["max_age"] = duration
    cookie["path"] = "/"
    cookie["httponly"] = True
    cookie["samesite"] = "lax"
    
    # if current_app.config["ENV"] == "production":
    #     cookie["domain"] = current_app.config[" COOKIE_DOMAIN"]
    #     cookie["secure"] = True
    # else:
    #     cookie["secure"] = False
    response.set_cookie(**cookie)
    return response


# function to set refresh cookie
def set_refresh_cookie(response: make_response, token, duration=3600) -> make_response:
    cookie = dict()
    
    cookie["key"] = "refresh_token"
    cookie["value"] = token
    cookie["max_age"] = duration
    cookie["path"] = "/"
    cookie["httponly"] = True
    cookie["samesite"] = "lax"
    
    # if current_app.config["ENV"] == "production":
    #     cookie["domain"] = current_app.config[" COOKIE_DOMAIN"]
    #     cookie["secure"] = True
    # else:
    #     cookie["secure"] = False
    response.set_cookie(**cookie)
    return response


