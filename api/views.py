from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from .utils.auth import Login, is_authenticated


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
def post(request):
    bool_authenticated, reason = is_authenticated(request)
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