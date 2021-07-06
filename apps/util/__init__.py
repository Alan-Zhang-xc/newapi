# -*- coding: utf-8 -*-
from flask import request, abort, g, Response

from apps.models.user_model import User
from exts import cache


def check_user():
    auth = request.headers.get("Authorization")
    if not auth:
        # Raises an :py:exc:`HTTPException` for the given status code or WSGI application
        abort(401)
        abort(Response('请先登录'))
    mobile = cache.get(auth)
    if not mobile:
        abort(401)
        abort(Response('invalid token'))
    user = User.query.filter(User.phone == mobile).first()
    if not user:
        abort(401)
        abort(Response('无效用户'))
    g.user = user


def login_required(func):
    def wrapper(*args, **kwargs):
        check_user()
        return func(*args, **kwargs)

    return wrapper
