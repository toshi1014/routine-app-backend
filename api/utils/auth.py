import time
from django.contrib.auth import authenticate
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
import jwt
import config
from .handle_db import MySQLHandler


def generate_token(id, old_decoded_token=None):
    user_row = MySQLHandler.fetch("users", {"id": id})

    if bool(old_decoded_token):
        following_list = old_decoded_token["followingList"]
        like_list = old_decoded_token["likeList"]
        favorite_list = old_decoded_token["favoriteList"]

        print(f"\n\treuse old token\n")

    ## if no old_decoded_token, get info from bd
    else:
        follow_row_list = MySQLHandler.fetchall(
            "follows",
            {"follower_user_id": id},
            allow_empty=True
        )
        following_list = [follow_row["followed_user_id"] for follow_row in follow_row_list]

        like_row_list = MySQLHandler.fetchall(
            "likes",
            {"user_id": id},
            allow_empty=True
        )
        like_list = [like_row["post_id"] for like_row in like_row_list]

        favorite_row_list = MySQLHandler.fetchall(
            "favorites",
            {"user_id": id},
            allow_empty=True
        )
        favorite_list = [favorite_row["post_id"] for favorite_row in favorite_row_list]

    timestamp = int(time.time()) + 60*60*24*7       ## expire in 1 weeek
    token = jwt.encode(
        {
            "id": id,
            "email": user_row["email"],
            "username": user_row["username"],
            "exp": timestamp,
            "followingList": following_list,
            "likeList": like_list,
            "favoriteList": favorite_list,
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
            row = MySQLHandler.fetch("users", {"email": email})
            id, username = row["id"], row["username"]
            token = generate_token(id)
            print("\n\tlogin successfully\n")

        return (token, None)


def is_authenticated(request, clear_cache=False):
    token = request.data['token']
    bool_authenticated = True
    id = None
    email = None
    username = None
    like_list = None
    favorite_list = None
    reason = None
    new_token = None

    try:
        decoded_token = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        id = decoded_token.get("id")
        email = decoded_token.get("email")
        username = decoded_token.get("username")
        exp = decoded_token.get("exp")
        like_list = decoded_token.get("likeList")
        favorite_list = decoded_token.get("favoriteList")

        if clear_cache:
            new_token = generate_token(id)
        else:
            new_token = generate_token(id, old_decoded_token=decoded_token)

        if int(exp) < int(time.time()):
            bool_authenticated = False
            reason = "expired token"
    except:
        ## signature verification failed
        bool_authenticated = False
        reason = "signature verification failed"

    return {
        "bool_authenticated": bool_authenticated,
        "id": id,
        "email": email,
        "username": username,
        "like_list": like_list,
        "favorite_list": favorite_list,
        "reason": reason,
        "new_token": new_token,
    }