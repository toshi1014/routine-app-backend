import os, datetime, pickle
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.response import Response
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from .utils.auth import Login, is_authenticated, generate_token
from .utils.handle_db import MySQLHandler
import config


EMAIL_TEMPLATE_FOLDER = "emails"


def basic_response(*deco_args, **deco_kwargs):
    def _basic_response(func):
        @api_view(["GET", "POST", "PUT", "DELETE"])
        def wrapper(*args, **kwargs):
            res = {
                "status": True,
                "token": "",
            }
            is_authenticated_dict = None

            # try:
            if True:        # DEBUG:
                if deco_kwargs["login_required"]:
                    is_authenticated_dict = is_authenticated(args[0]) ## args[0] == request

                    res["status"] = is_authenticated_dict["bool_authenticated"]
                    res["token"] = is_authenticated_dict["new_token"]

                    if is_authenticated_dict["bool_authenticated"]:
                        res.update({
                            "contents": func(
                                *args, **kwargs, is_authenticated_dict=is_authenticated_dict
                            ),
                        })
                    else:
                        res.update({"errorMessage": is_authenticated_dict["reason"]})
                else:
                    res.update({"contents": func(*args, **kwargs)})

            # except Exception as e:
            else:
                # print("\n\tErr:", e, "\n")

                error_report(func, e, is_authenticated_dict, args[0]) ## args[0] == request
                res["status"] = False
                res.update({"errorMessage": "backend error"})

            return Response([res])
        return wrapper
    return _basic_response


def error_report(func, exception, is_authenticated_dict, request):
    subject = "Backend Error"
    message = f"""
func\t: {str(func)}
err\t: {str(exception)}
req\t: {str(request)}
data\t: {request.data}
    """

    django_send_mail(
        subject=subject,
        message=message,
        from_email=config.EMAIL_HOST_USER,
        recipient_list=[config.EMAIL_ADMIN],
    )


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


@basic_response(login_required=False)
def is_unique(request):
    column, val = request.data["column"], request.data["val"]

    # TODO: check whether unique
    bool_unique = False
    return  { "boolUnique": bool_unique }


@basic_response(login_required=False)
def signup(request):
    email, password, username = \
        request.data["email"], request.data["password"], request.data["username"]

    print("\tparams")
    print("\n\t", email, password, username)

    user = User.objects.create_user(username=email, password=password)
    user = authenticate(request, username=email, password=password)
    MySQLHandler.insert("users", {"email": email, "username": username})
    id = MySQLHandler.fetch("users", {"email": email})["id"]
    token = generate_token(id)
    print("created successfully")

    return {
        "newToken": token,
    }


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


def get_posted_list(user_row):
    return get_pack_content_list(
        "post_contents",
        MySQLHandler.fetchall(
            "posts",
            {"contributor_id": user_row["id"]},
            allow_empty=True,
        ),
        user_row,
        allow_empty=True,
    )


def get_favorite_list(user_row):
    favorite_post_id_list = MySQLHandler.fetchall(
        "favorites",
        {"user_id": user_row["id"]},
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

    return favorite_list

def get_draft_list(user_row):
    return get_pack_content_list(
        "draft_contents",
        MySQLHandler.fetchall(
            "drafts",
            {"contributor_id": user_row["id"]},
            allow_empty=True,
        ),
        user_row,
        allow_empty=True,
    )


@basic_response(login_required=False)
def mypage(request, user_id):
    user_row = MySQLHandler.fetch(
        "users", {"id": user_id}
    )

    return {
        "header": get_mypage_header(user_row),
        "postedList": get_posted_list(user_row),
        "favoriteList": get_favorite_list(user_row),
    }


@basic_response(login_required=True)
def mypage_login(request, is_authenticated_dict):
    user_row = MySQLHandler.fetch(
        "users", {"id": is_authenticated_dict["id"]}
    )

    return {
        "header": get_mypage_header(user_row),
        "postedList": get_posted_list(user_row),
        "favoriteList": get_favorite_list(user_row),
        "draftList": get_draft_list(user_row),
    }


@basic_response(login_required=True)
def update_user_info(request, is_authenticated_dict):
    column = request.data["column"]
    val = request.data["val"]
    MySQLHandler.update(
        "users",
        { "id": is_authenticated_dict["id"]},
        dict_update_column_val={column: val}
    )

    return {}


@basic_response(login_required=True)
def post_or_draft(request, is_authenticated_dict):
    print("\n\t", request.data, "\n")
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


    contents_title = {
        "contributor_id": is_authenticated_dict["id"],
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
            MySQLHandler.delete("drafts", {"id": post_id})
            MySQLHandler.delete("draft_contents", {"post_id": post_id})
        elif bool_post2draft:
            MySQLHandler.delete("posts", {"id": post_id})
            MySQLHandler.delete("post_contents", {"post_id": post_id})

    return {}


@basic_response(login_required=False)
def get_contents(request, post_id):
    print("\n\t", post_id, "\n")

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

    return {
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
    }


@basic_response(login_required=True)
def get_draft(request, is_authenticated_dict):
    draft_id = request.data["id"]
    user_row = MySQLHandler.fetch("users", {"id": is_authenticated_dict["id"]})
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

    return {
        "header": {
            "title": draft_row["title"],
            "desc": draft_row["description"],
            "hashtagList": draft_row["hashtag_list"].split(","),
            "like": draft_row["like_num"],
            "contributor": user_row["username"],
            "lastUpdated": draft_row["last_updated"],
        },
        "elementList": element_list,
    }


@basic_response(login_required=True)
def delete_post_or_draft(request, is_authenticated_dict):
    postOrDraft = request.data["postOrDraft"]
    id = request.data["id"]

    print("\n\tid:", id, "\n")

    if postOrDraft == "post":
        MySQLHandler.delete("posts", {"id": id})
        MySQLHandler.delete("post_contents", {"post_id": id})
    elif postOrDraft == "draft":
        MySQLHandler.delete("drafts", {"id": id})
        MySQLHandler.delete("draft_contents", {"post_id": id})
    else:
        raise ValueError(f"unknown value {postOrDraft}")

    return {}


@basic_response(login_required=False)
def search_results(request, keyword, target, page):
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

    return {
        "resultList": result_list,
        "pageLength": page_length,
    }


def follow_base(request, user_id, follow_or_unfollow):
    target_user_id = request.data["targetUserId"]

    if follow_or_unfollow == "follow":
        pfunc = MySQLHandler.insert
        diff = 1
    elif follow_or_unfollow == "unfollow":
        pfunc = MySQLHandler.delete
        diff = -1
    else:
        raise ValueError(f"unknown follow_or_unfollow {follow_or_unfollow}")

    pfunc(
        "follows",
        {
            "followed_user_id": target_user_id,
            "follower_user_id": user_id,
        }
    )

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

    ## generate new token with updated rows
    return is_authenticated(request, clear_cache=True)


@basic_response(login_required=True)
def follow(request, is_authenticated_dict):
    is_authenticated_dict = follow_base(request, is_authenticated_dict["id"], "follow")

    return {
        "newToken": is_authenticated_dict["new_token"]
    }


@basic_response(login_required=True)
def unfollow(request, is_authenticated_dict):
    is_authenticated_dict = follow_base(request, is_authenticated_dict["id"], "unfollow")

    return {
        "newToken": is_authenticated_dict["new_token"]
    }


@basic_response(login_required=False)
def get_following_or_followers(request, user_id, following_or_follwers):
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

    return {
        "userList": user_list,
    }


def like_base(request, user_id, like_or_unlike):
    post_id = request.data["postId"]

    if like_or_unlike == "like":
        pfunc = MySQLHandler.insert
        diff = 1
    elif like_or_unlike == "unlike":
        pfunc = MySQLHandler.delete
        diff = -1
    else:
        raise ValueError(f"unknown like_or_unlike {like_or_unlike}")

    pfunc(
        "likes",
        {
            "user_id": user_id,
            "post_id": post_id
        }
    )

    target_post_row = MySQLHandler.fetch("posts", {"id": post_id})
    MySQLHandler.update(
        "posts",
        {"id": post_id},
        dict_update_column_val={
            "like_num": target_post_row["like_num"] + diff
        }
    )

    ## generate new token with updated rows
    return is_authenticated(request, clear_cache=True)


@basic_response(login_required=True)
def like(request, is_authenticated_dict):
    post_id = request.data["postId"]

    if not (post_id in is_authenticated_dict["like_list"]):
        is_authenticated_dict = like_base(request, is_authenticated_dict["id"], "like")

    return {
        "newToken": is_authenticated_dict["new_token"]
    }


@basic_response(login_required=True)
def unlike(request, is_authenticated_dict):
    is_authenticated_dict = like_base(request, is_authenticated_dict["id"], "unlike")

    return {
        "newToken": is_authenticated_dict["new_token"]
    }


def favorite_base(request, user_id, favorite_or_unfavorite):
    post_id = request.data["postId"]

    if favorite_or_unfavorite == "favorite":
        pfunc = MySQLHandler.insert
    elif favorite_or_unfavorite == "unfavorite":
        pfunc = MySQLHandler.delete

    pfunc(
        "favorites",
        {
            "user_id": user_id,
            "post_id": post_id
        }
    )

    ## generate new token with updated rows
    return is_authenticated(request, clear_cache=True)


@basic_response(login_required=True)
def favorite(request, is_authenticated_dict):
    post_id = request.data["postId"]

    if not (post_id in is_authenticated_dict["favorite_list"]):
        is_authenticated_dict = favorite_base(request, is_authenticated_dict["id"], "favorite")

    return {
        "newToken": is_authenticated_dict["new_token"]
    }


@basic_response(login_required=True)
def unfavorite(request, is_authenticated_dict):
    is_authenticated_dict = favorite_base(request, is_authenticated_dict["id"], "unfavorite")

    return {
        "newToken": is_authenticated_dict["new_token"]
    }



@basic_response(login_required=False)
def send_email(request):
    recipient = request.data["recipient"]
    purpose = request.data["purpose"]
    context = request.data["context"]

    if purpose == "auth":
        template_filepath = os.path.join(EMAIL_TEMPLATE_FOLDER, "auth.html")
        subject = "Activate your account!"
    else:
        raise Exception(f"unknown purpose {purpose}")

    html_content = render_to_string(template_filepath, context)

    django_send_mail(
        subject=subject,
        message=strip_tags(html_content),
        from_email=config.EMAIL_HOST_USER,
        recipient_list=[recipient],
        html_message=html_content,
    )
    return {}


# DEBUG: below
@api_view(["POST"])
def post_debug(request):
    is_authenticated_dict = is_authenticated(request)
    if is_authenticated_dict["bool_authenticated"]:
        res = [{"status": True, "val":112}]
    else:
        res = [{"status": False, "reason": is_authenticated_dict["reason"]}]
    return Response(res)


@basic_response(login_required=False)
def debug(request):
    res = {"message": f"Hello, World!"}
    return res


@api_view(["GET"])
def delete_users(request):
    from django.contrib.auth.models import User
    users = User.objects.all()
    for user in users:
        if user.email != "a@gmail.com":
            user.delete()

    res = [{"status": True}]

    return Response(res)