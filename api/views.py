from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from .utils.auth import Login, is_authenticated, generate_token
from .utils.handle_db import MySQLHandler


@api_view(["POST"])
@authentication_classes([Login])
def login(request):
    if (request.user != None):
        status = True
    else:
        status = False

    res = [{
        "status": status,
        "token": str(request.user),
    }]

    return Response(res)


@api_view(["POST"])
def is_unique(request):
    column, val = request.data["column"], request.data["val"]

    # TODO: check whether unique
    res = [{
        "status": False,
    }]

    return Response(res)


@api_view(["POST"])
def signup(request):
    email, password, username = \
        request.data["email"], request.data["password"], request.data["username"]

    print("\tparams")
    print("\n\t", email, password, username)

    try:
        user = User.objects.create_user(username=email, password=password)
        user = authenticate(request, username=email, password=password)
        token = generate_token(user.pk)
        status = True
        MySQLHandler.insert("users", {"email": email})
        print("created successfully")
    except Exception as e:
        print("\n\tErr:", e, "\n")
        status = False
        token = None

    res = [{
        "status": status,
        "token": token,
    }]

    return Response(res)


@api_view(["POST"])
def mypage_login(request):
    bool_authenticated, reason, new_token = is_authenticated(request)

    res = [{
        "status": bool_authenticated,
        "token": new_token
    }]

    if bool_authenticated:
        res[0].update({"username": "John Doe"})
    else:
        res[0].update({"errorMessage": reason})

    return Response(res)


@api_view(["POST"])
def post(request):
    bool_authenticated, reason, new_token = is_authenticated(request)
    if bool_authenticated:
        res = [{"status": True, "val":112}]
    else:
        res = [{"status": False, "reason": reason}]
    return Response(res)


@api_view(["GET", "POST"])
def debug(request):
    if request.method == "GET":
        res = [{"message": "Hello World"}]

    elif request.method == "POST":
        name = request.data["name"]
        res = [{"message": f"Hello, {name}!"}]

    return Response(res)