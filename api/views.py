import datetime
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from .utils.auth import Login, is_authenticated, generate_token
from .utils.handle_db import MySQLHandler
import config


def get_pack_content_list(table, xx_row_list, user_row=None, allow_empty=True):
    xx_list = []

    xx_contents_row_list = [
        MySQLHandler.fetch(
            table,
            {
                "post_id": xx_row["id"],
                "step_num": 1
            },
            allow_empty,
        ) for xx_row in xx_row_list
    ]

    for xx_row, xx_contents_row in zip(xx_row_list, xx_contents_row_list):
        ## if user_row is not provided
        if not bool(user_row):
            user_row_now = MySQLHandler.fetch(
                "users",
                {"id": xx_row["contributor_id"]},
                allow_empty=False,
            )
        else:
            user_row_now = user_row

        xx_list.append({
            "id": xx_row["id"],
            "contributor": user_row_now["username"],
            "contributorId": user_row_now["id"],
            "title": xx_row["title"],
            "desc": xx_row["description"],
            "titleStep1": xx_contents_row["title"],
            "descStep1": xx_contents_row["description"],
            "like": xx_row["like_num"],
        })

    return xx_list


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
        token = generate_token(id)
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


def get_mypage_header(user_row):
    header = {
        "email": user_row["email"],
        "username": user_row["username"],
        "statusMessage": user_row["status_message"],
        "hashtagList": user_row["hashtag_list"].split(","),
        "followingNum": user_row["following_num"],
        "followersNum": user_row["followers_num"],
    }
    return header;


@api_view(["GET"])
def mypage(request, user_id):
    res = [{
        "status": True,
        "token": "",
    }]

    # try:
    if True:
        user_row = MySQLHandler.fetch(
            "users", {"id": user_id}
        )

        posted_list = get_pack_content_list(
            "post_contents",
            MySQLHandler.fetchall(
                "posts",
                {"contributor_id": user_id},
                allow_empty=True,
            ),
            user_row,
            allow_empty=True,
        )

        favorite_post_id_list = MySQLHandler.fetchall(
            "favorites",
            {"user_id": user_id},
            allow_empty=True,
        )
        favorite_list = []
        for favorite_post_id in favorite_post_id_list:
            favorite_list += get_pack_content_list(
                "post_contents",
                MySQLHandler.fetchall(
                    "posts",
                    {"id": favorite_post_id["post_id"]},
                ),
                allow_empty=True,
            )

        res[0].update({
            "contents":{
                "header": get_mypage_header(user_row),
                "postedList": posted_list,
                "favoriteList": favorite_list,
            }
        })
    # except Exception as e:
    else:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

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

            posted_list = get_pack_content_list(
                "post_contents",
                MySQLHandler.fetchall(
                    "posts",
                    {"contributor_id": dict_is_authenticated["id"]},
                    allow_empty=True,
                ),
                user_row,
                allow_empty=True,
            )

            favorite_post_id_list = MySQLHandler.fetchall(
                "favorites",
                {"user_id": dict_is_authenticated["id"]},
                allow_empty=True,
            )
            favorite_list = []
            for favorite_post_id in favorite_post_id_list:
                favorite_list += get_pack_content_list(
                    "post_contents",
                    MySQLHandler.fetchall(
                        "posts",
                        {"id": favorite_post_id["post_id"]},
                    ),
                    allow_empty=True,
                )

            draft_list = get_pack_content_list(
                "draft_contents",
                MySQLHandler.fetchall(
                    "drafts",
                    {"contributor_id": dict_is_authenticated["id"]},
                    allow_empty=True,
                ),
                user_row,
                allow_empty=True,
            )

            res[0].update({
                "contents":{
                    "header": get_mypage_header(user_row),
                    "postedList": posted_list,
                    "favoriteList": favorite_list,
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
            MySQLHandler.update("users", {"id": id}, dict_update_column_val={column: val})

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

    print("\n\t", request.data, "\n")

    # try:
    if True:
        if dict_is_authenticated["bool_authenticated"]:
            post_or_draft = request.data["postOrDraft"]
            post_id = request.data["postId"]    ## None or int
            bool_edited_draft = request.data["boolEditedDraft"]
            title = request.data["title"]
            desc = request.data["desc"]
            hashtag_list = request.data["hashtagLabelList"]
            routine_element_list = request.data["routineElements"]

            bool_draft2post = bool_edited_draft & (post_or_draft == "post")
            bool_post2draft = (not bool_edited_draft) & (post_or_draft == "draft") & bool(post_id)

            if post_or_draft == "post":
                title_table = "posts"
                contents_table = "post_contents"
            elif post_or_draft == "draft":
                title_table = "drafts"
                contents_table = "draft_contents"
            else:
                raise Exception(f"unknown post_or_draft {post_or_draft}")


            user_id = MySQLHandler.fetch("users", {"email": dict_is_authenticated["email"]})["id"]
            contents_title = {
                "contributor_id": user_id,
                "title": title,
                "description": desc,
                "last_updated": str(datetime.datetime.now())[:-7],
                "hashtag_list": ",".join(hashtag_list),
            }


            ## if just update & not draft2post & not post2draft
            if bool(post_id) & (not bool_draft2post) & (not bool_post2draft):
                MySQLHandler.update(
                    title_table, {"id": post_id}, contents_title
                )
                for idx, routine_element in enumerate(routine_element_list):
                    MySQLHandler.update(
                        contents_table,
                        {"post_id": post_id, "step_num": idx+1},
                        {
                            "title": routine_element["title"],
                            "subtitle": routine_element["subtitle"],
                            "description": routine_element["desc"],
                        }
                    )

            ## if new post
            else:
                lastrowid = MySQLHandler.insert(
                    title_table, contents_title
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

                if bool_draft2post:
                    ## delete draft
                    MySQLHandler.delete("drafts", "id", post_id)
                    MySQLHandler.delete("draft_contents", "post_id", post_id)
                elif bool_post2draft:
                    MySQLHandler.delete("posts", "id", post_id)
                    MySQLHandler.delete("post_contents", "post_id", post_id)

        else:
            res[0].update({"errorMessage": dict_is_authenticated["reason"]})

    # except Exception as e:
    else:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

    return Response(res)


@api_view(["GET"])
def get_contents(request, post_id):
    res = [{
        "status": True,
        "token": "",
    }]

    print("\n\t", post_id, "\n")

    # try:
    if True:
        post_row = MySQLHandler.fetch("posts", {"id": post_id})
        user_row = MySQLHandler.fetch("users", {"id": post_row["contributor_id"]})

        raw_post_contents_row_list = MySQLHandler.fetchall(
            "post_contents", {"post_id": post_row["id"]},
        )

        element_list = []

        post_contents_row_list = sorted(raw_post_contents_row_list, key=lambda kv: kv["step_num"])

        for post_contents_row in post_contents_row_list:
            element_list.append({
                "title": post_contents_row["title"],
                "subtitle": post_contents_row["subtitle"],
                "desc": post_contents_row["description"],
                "imagePath": "logo192.png",     # TEMP: image path
            })

        res[0].update({
            "contents":{
                    "header": {
                        "title": post_row["title"],
                        "desc": post_row["description"],
                        "hashtagList": post_row["hashtag_list"].split(","),
                        "like": post_row["like_num"],
                        "contributor": user_row["username"],
                        "contributorId": user_row["id"],
                        "lastUpdated": post_row["last_updated"],
                    },
                    "elementList": element_list,
                },
            }
        )

    # except Exception as e:
    else:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

    return Response(res)


@api_view(["POST"])
def get_draft(request):
    dict_is_authenticated = is_authenticated(request)
    res = [{
        "status": dict_is_authenticated["bool_authenticated"],
        "token": dict_is_authenticated["new_token"],
    }]

    # try:
    if True:
        if dict_is_authenticated["bool_authenticated"]:
            draft_id = request.data["id"]
            user_row = MySQLHandler.fetch("users", {"email": dict_is_authenticated["email"]})
            draft_row = MySQLHandler.fetch("drafts", {"id": draft_id, "contributor_id": user_row["id"]})

            raw_draft_contents_row_list = MySQLHandler.fetchall(
                "draft_contents", {"post_id": draft_row["id"]},
            )

            element_list = []

            draft_contents_row_list = sorted(raw_draft_contents_row_list, key=lambda kv: kv["step_num"])

            for draft_contents_row in draft_contents_row_list:
                element_list.append({
                    "title": draft_contents_row["title"],
                    "subtitle": draft_contents_row["subtitle"],
                    "desc": draft_contents_row["description"],
                    "imagePath": "logo192.png",     # TEMP: image path
                })

            res[0].update({
                "contents":{
                        "header": {
                            "title": draft_row["title"],
                            "desc": draft_row["description"],
                            "hashtagList": draft_row["hashtag_list"].split(","),
                            "like": draft_row["like_num"],
                            "contributor": user_row["username"],
                            "lastUpdated": draft_row["last_updated"],
                        },
                        "elementList": element_list,
                    },
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
def delete_post_or_draft(request):
    dict_is_authenticated = is_authenticated(request)
    res = [{
        "status": dict_is_authenticated["bool_authenticated"],
        "token": dict_is_authenticated["new_token"],
    }]

    try:
        if dict_is_authenticated["bool_authenticated"]:
            postOrDraft = request.data["postOrDraft"]
            id = request.data["id"]

            if postOrDraft == "post":
                MySQLHandler.delete("posts", "id", id)
                MySQLHandler.delete("post_contents", "post_id", id)
            elif postOrDraft == "draft":
                MySQLHandler.delete("drafts", "id", id)
                MySQLHandler.delete("draft_contents", "post_id", id)
            else:
                raise ValueError(f"unknown value {postOrDraft}")

        else:
            res[0].update({"errorMessage": dict_is_authenticated["reason"]})

    except Exception as e:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

    return Response(res)


@api_view(["GET"])
def search_results(request, keyword, target, page):
    res = [{
        "status": True,
        "token": "",
    }]

    # try:
    if True:
        # COMBAK: use target
        raw_result_row_list = MySQLHandler.search(
            keyword,
            {
                "posts": ["title", "description"],
                "post_contents": ["title", "subtitle", "description"]
            },
        )

        result_row_list = raw_result_row_list[
            (page - 1)* config.POSTS_PER_PAGE*page :
            config.POSTS_PER_PAGE * page
        ]

        result_list = get_pack_content_list(
            "post_contents",
            result_row_list,
            allow_empty=True,
        )

        page_length = len(raw_result_row_list)//config.POSTS_PER_PAGE
        if page_length == 0:
            page_length = 1

        res[0].update({
            "contents":{
                    "resultList": result_list,
                    "pageLength": page_length,
                },
            }
        )
    # except Exception as e:
    else:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

    return Response(res)


def follow_base(user_id, target_user_id, follow_or_unfollow):
    if follow_or_unfollow == "follow":
        diff = 1
    elif follow_or_unfollow == "unfollow":
        diff = -1
    else:
        raise ValueError(f"unknown follow_or_unfollow {follow_or_unfollow}")

    ## update followed one's row
    target_user_row = MySQLHandler.fetch("users", {"id": target_user_id})
    MySQLHandler.update(
        "users",
        {"id": target_user_id},
        dict_update_column_val={
            "followers_num": target_user_row["followers_num"] + diff
        }
    )

    ## update following one's row
    user_row = MySQLHandler.fetch("users", {"id": user_id})

    MySQLHandler.update(
        "users",
        {"id": user_id},
        dict_update_column_val={
            "following_num": user_row["following_num"] + diff
        }
    )


@api_view(["POST"])
def follow(request):
    dict_is_authenticated = is_authenticated(request)
    res = [{
        "status": dict_is_authenticated["bool_authenticated"],
        "token": dict_is_authenticated["new_token"],
    }]

    # try:
    if True:
        if dict_is_authenticated["bool_authenticated"]:
            target_user_id = request.data["targetUserId"]

            MySQLHandler.insert(
                "follows",
                {
                    "followed_user_id": target_user_id,
                    "follower_user_id": dict_is_authenticated["id"]
                }
            )

            follow_base(dict_is_authenticated["id"], target_user_id, "follow")


            ## generate new token with updated rows
            dict_is_authenticated = is_authenticated(request, clear_cache=True)
            res[0].update({"token": dict_is_authenticated["new_token"]})

        else:
            res[0].update({"errorMessage": dict_is_authenticated["reason"]})

    # except Exception as e:
    else:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

    return Response(res)


@api_view(["POST"])
def unfollow(request):
    dict_is_authenticated = is_authenticated(request, clear_cache=True)
    res = [{
        "status": dict_is_authenticated["bool_authenticated"],
        "token": dict_is_authenticated["new_token"],
    }]

    # try:
    if True:
        if dict_is_authenticated["bool_authenticated"]:
            target_user_id = request.data["targetUserId"]

            MySQLHandler.delete(
                "follows",
                {
                    "followed_user_id": target_user_id,
                    "follower_user_id": dict_is_authenticated["id"]
                }
            )

            follow_base(dict_is_authenticated["id"], target_user_id, "unfollow")

            ## generate new token with updated rows
            dict_is_authenticated = is_authenticated(request, clear_cache=True)
            res[0].update({"token": dict_is_authenticated["new_token"]})

        else:
            res[0].update({"errorMessage": dict_is_authenticated["reason"]})

    # except Exception as e:
    else:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

    return Response(res)


@api_view(["GET"])
def get_following_or_followers(request, user_id, following_or_follwers):
    res = [{
        "status": True,
        "token": "",
    }]

    # try:
    if True:
        if following_or_follwers == "following":
            search_column = "follower_user_id"
            target_column = "followed_user_id"
        elif following_or_follwers == "followers":
            search_column = "followed_user_id"
            target_column = "follower_user_id"
        else:
            raise Exception("unknown val")

        user_list = [
            {
                "username": MySQLHandler.fetch("users", {"id": row[target_column]})["username"],
                "userId": row[target_column],
            }
            for row in MySQLHandler.fetchall(
                "follows",
                {search_column: user_id},
            )
        ]

        res[0].update({
            "contents": user_list,
            }
        )
    # except Exception as e:
    else:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

    return Response(res)


def like_base(user_id, post_id, like_or_unlike):
    if like_or_unlike == "like":
        diff = 1
    elif like_or_unlike == "unlike":
        diff = -1
    else:
        raise ValueError(f"unknown like_or_unlike {like_or_unlike}")

    target_post_row = MySQLHandler.fetch("posts", {"id": post_id})
    MySQLHandler.update(
        "posts",
        {"id": post_id},
        dict_update_column_val={
            "like_num": target_post_row["like_num"] + diff
        }
    )


@api_view(["POST"])
def like(request):
    dict_is_authenticated = is_authenticated(request)
    res = [{
        "status": dict_is_authenticated["bool_authenticated"],
        "token": dict_is_authenticated["new_token"],
    }]

    # try:
    if True:
        if dict_is_authenticated["bool_authenticated"]:
            post_id = request.data["postId"]

            if not (post_id in dict_is_authenticated["like_list"]):
                MySQLHandler.insert(
                    "likes",
                    {
                        "user_id": dict_is_authenticated["id"],
                        "post_id": post_id
                    }
                )

                like_base(dict_is_authenticated["id"], post_id, "like")

                ## generate new token with updated rows
                dict_is_authenticated = is_authenticated(request, clear_cache=True)
                res[0].update({"token": dict_is_authenticated["new_token"]})

        else:
            res[0].update({"errorMessage": dict_is_authenticated["reason"]})

    # except Exception as e:
    else:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

    return Response(res)


@api_view(["POST"])
def unlike(request):
    dict_is_authenticated = is_authenticated(request, clear_cache=True)
    res = [{
        "status": dict_is_authenticated["bool_authenticated"],
        "token": dict_is_authenticated["new_token"],
    }]

    # try:
    if True:
        if dict_is_authenticated["bool_authenticated"]:
            post_id = request.data["postId"]

            MySQLHandler.delete(
                "likes",
                {
                    "user_id": dict_is_authenticated["id"],
                    "post_id": post_id
                }
            )

            like_base(dict_is_authenticated["id"], post_id, "unlike")

            ## generate new token with updated rows
            dict_is_authenticated = is_authenticated(request, clear_cache=True)
            res[0].update({"token": dict_is_authenticated["new_token"]})

        else:
            res[0].update({"errorMessage": dict_is_authenticated["reason"]})

    # except Exception as e:
    else:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

    return Response(res)


@api_view(["POST"])
def favorite(request):
    dict_is_authenticated = is_authenticated(request)
    res = [{
        "status": dict_is_authenticated["bool_authenticated"],
        "token": dict_is_authenticated["new_token"],
    }]

    # try:
    if True:
        if dict_is_authenticated["bool_authenticated"]:
            post_id = request.data["postId"]

            if not (post_id in dict_is_authenticated["favorite_list"]):
                MySQLHandler.insert(
                    "favorites",
                    {
                        "user_id": dict_is_authenticated["id"],
                        "post_id": post_id
                    }
                )

                ## generate new token with updated rows
                dict_is_authenticated = is_authenticated(request, clear_cache=True)
                res[0].update({"token": dict_is_authenticated["new_token"]})

        else:
            res[0].update({"errorMessage": dict_is_authenticated["reason"]})

    # except Exception as e:
    else:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

    return Response(res)


@api_view(["POST"])
def unfavorite(request):
    dict_is_authenticated = is_authenticated(request, clear_cache=True)
    res = [{
        "status": dict_is_authenticated["bool_authenticated"],
        "token": dict_is_authenticated["new_token"],
    }]

    # try:
    if True:
        if dict_is_authenticated["bool_authenticated"]:
            post_id = request.data["postId"]

            MySQLHandler.delete(
                "favorites",
                {
                    "user_id": dict_is_authenticated["id"],
                    "post_id": post_id
                }
            )

            ## generate new token with updated rows
            dict_is_authenticated = is_authenticated(request, clear_cache=True)
            res[0].update({"token": dict_is_authenticated["new_token"]})

        else:
            res[0].update({"errorMessage": dict_is_authenticated["reason"]})

    # except Exception as e:
    else:
        print("\n\tErr:", e, "\n")
        res[0]["status"] = False
        res[0].update({"errorMessage": "backend error"})

    return Response(res)


# DEBUG: below
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


@api_view(["GET"])
def delete_users(request):
    from django.contrib.auth.models import User
    users = User.objects.all()
    for user in users:
        if user.email != "a@gmail.com":
            user.delete()

    res = [{"status": True}]

    return Response(res)