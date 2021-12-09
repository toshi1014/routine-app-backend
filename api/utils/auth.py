import time
from django.contrib.auth import authenticate
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
import jwt
import config


def generate_token(user):
    timestamp = int(time.time()) + 60*60*24*7       ## expire in 1 weeek
    token = jwt.encode(
        {
            "id": user.pk,
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
            token = generate_token(user)
            print("\n\tlogin successfully\n")

        return (token, None)


def is_authenticated(request):
    token = request.data['token']
    try:
        decoded_token = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    except:
        ## signature verification failed
        return False, "signature verification failed"

    id, exp = decoded_token.get("id"), decoded_token.get("exp")

    if int(exp) < int(time.time()):
        print("expired token")
        return False, "expired token"

    return True, None