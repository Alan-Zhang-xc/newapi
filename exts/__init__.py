# -*- coding: utf-8 -*-
from flask_caching import Cache
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy 数据库对象
db = SQLAlchemy()

# 跨域
cors = CORS()

# redis缓存
cache = Cache()