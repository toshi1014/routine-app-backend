import datetime
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
        MySQLHandler.insert("users", {"email": email, "username": username})
        id = MySQLHandler.fetch("users", {"email": email})["id"]
        token = generate_token(id, email, username)
        status = True
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
    dict_is_authenticated = is_authenticated(request)

    res = [{
        "status": dict_is_authenticated["bool_authenticated"],
        "token": dict_is_authenticated["new_token"],
    }]

    # try:
    if True:
        if dict_is_authenticated["bool_authenticated"]:
            user_row = MySQLHandler.fetch(
                "users", {"email": dict_is_authenticated["email"]}
            )

            posted_list = []
            draft_list = []

            component_list = [
                {
                    "title_table": "posts",
                    "contents_table": "post_contents",
                    "xx_list": posted_list,
                },
                {
                    "title_table": "drafts",
                    "contents_table": "draft_contents",
                    "xx_list": draft_list,
                },
            ]

            for component in component_list:
                xx_row_list = MySQLHandler.fetchall(
                    component["title_table"],
                    {"contributor_id": dict_is_authenticated["id"]},
                    allow_empty=True,
                )

                xx_contents_row_list = [
                    MySQLHandler.fetch(
                        component["contents_table"],
                        {
                            "post_id": xx_row["id"],
                            "step_num": 1
                        },
                        allow_empty=True,
                    ) for xx_row in xx_row_list
                ]

                for xx_row, xx_contents_row in zip(xx_row_list, xx_contents_row_list):
                    component["xx_list"].append({
                        "id": xx_row["id"],
                        "contributor": user_row["username"],
                        "title": xx_row["title"],
                        "desc": xx_row["description"],
                        "titleStep1": xx_contents_row["title"],
                        "descStep1": xx_contents_row["description"],
                    })


            res[0].update({
                "contents":{
                    "header": {
                        "email": user_row["email"],
                        "username": user_row["username"],
                        "statusMessage": user_row["status_message"],
                        "hashtagList": user_row["hashtag_list"].split(","),
                        "followingNum": user_row["following_num"],
                        "followersNum": user_row["followers_num"],
                    },
                    "postedList": posted_list,
                    "draftList": draft_list,
                }
            })
        else:
            res[0].update({"errorMessage": dict_is_authenticated["reason"]})
    # except Exception as e:
    else:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

    return Response(res)


@api_view(["PUT"])
def update_user_info(request):
    dict_is_authenticated = is_authenticated(request)
    res = [{
        "status": dict_is_authenticated["bool_authenticated"],
        "token": dict_is_authenticated["new_token"],
    }]

    try:
        if dict_is_authenticated["bool_authenticated"]:
            column = request.data["column"]
            val = request.data["val"]
            id = MySQLHandler.fetch("users", {"email": dict_is_authenticated["email"]})["id"]
            MySQLHandler.update("users", key="id", val=id, dict_update_column_val={column: val})

        else:
            res[0].update({"errorMessage": dict_is_authenticated["reason"]})

    except Exception as e:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

    return Response(res)


@api_view(["POST"])
def post_or_draft(request):
    dict_is_authenticated = is_authenticated(request)
    res = [{
        "status": dict_is_authenticated["bool_authenticated"],
        "token": dict_is_authenticated["new_token"],
    }]

    # try:
    if True:
        if dict_is_authenticated["bool_authenticated"]:
            post_or_draft = request.data["postOrDraft"]
            title = request.data["title"]
            desc = request.data["desc"]
            hashtag_list = request.data["hashtagLabelList"]
            routine_element_list = request.data["routineElements"]

            if post_or_draft == "post":
                title_table = "posts"
                contents_table = "post_contents"
            elif post_or_draft == "draft":
                title_table = "drafts"
                contents_table = "draft_contents"
            else:
                raise Exception(f"unknown post_or_draft {post_or_draft}")


            user_id = MySQLHandler.fetch("users", {"email": dict_is_authenticated["email"]})["id"]
            lastrowid = MySQLHandler.insert(
                title_table,
                {
                    "contributor_id": user_id,
                    "title": title,
                    "description": desc,
                    "last_updated": str(datetime.datetime.now())[:-7],
                    "hashtag_list": ",".join(hashtag_list),
                }
            )

            for idx, routine_element in enumerate(routine_element_list):
                MySQLHandler.insert(
                    contents_table,
                    {
                        "post_id": lastrowid,
                        "step_num": idx + 1,        ## idx to order
                        "title": routine_element["title"],
                        "subtitle": routine_element["subtitle"],
                        "description": routine_element["desc"],
                    }
                )

        else:
            res[0].update({"errorMessage": dict_is_authenticated["reason"]})

    # except Exception as e:
    else:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

    return Response(res)


@api_view(["POST"])
def post_debug(request):
    dict_is_authenticated = is_authenticated(request)
    if dict_is_authenticated["bool_authenticated"]:
        res = [{"status": True, "val":112}]
    else:
        res = [{"status": False, "reason": dict_is_authenticated["reason"]}]
    return Response(res)


@api_view(["GET", "POST"])
def debug(request):
    if request.method == "GET":
        res = [{"message": "Hello World"}]

    elif request.method == "POST":
        name = request.data["name"]
        res = [{"message": f"Hello, {name}!"}]

    return Response(res)