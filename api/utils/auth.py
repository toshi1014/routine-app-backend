import time
from django.contrib.auth import authenticate
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
import jwt
import config
from .handle_db import MySQLHandler


def generate_token(id, email, username):
    timestamp = int(time.time()) + 60*60*24*7       ## expire in 1 weeek
    token = jwt.encode(
        {
            "id": id,
            "email": email,
            "username": username,
            "exp": timestamp,
        },
        config.SECRET_KEY,
        algorithm="HS256"
    )

    return token


class Login(BaseAuthentication):
    def authenticate(self, request):
        email = request.data['email']
        password = request.data['password']
        user = authenticate(request, username=email, password=password)

        print("\n\temail:", email, "\tpassword:", password, "\n")

        if user is None:
            token = None
            print("\n\tlogin failed\n")
        else:
            username = MySQLHandler.fetch("users", key="email", val=email)
            token = generate_token(user.pk, email=user.username, username=user.username)
            print("\n\tlogin successfully\n")

        return (token, None)


def is_authenticated(request):
    token = request.data['token']
    bool_authenticated = True
    id = None
    email = None
    username = None
    reason = None
    new_token = None

    try:
        decoded_token = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        id = decoded_token.get("id")
        email = decoded_token.get("email")
        username = decoded_token.get("username")
        new_token = generate_token(id, email, username)
    except:
        ## signature verification failed
        bool_authenticated = False
        reason = "signature verification failed"

    exp = decoded_token.get("exp")

    if int(exp) < int(time.time()):
        bool_authenticated = False
        reason = "expired token"

    return {
        "bool_authenticated": bool_authenticated,
        "id": id,
        "email": email,
        "username": username,
        "reason": reason,
        "new_token": new_token,
    }