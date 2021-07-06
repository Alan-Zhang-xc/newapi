# -*- coding: utf-8 -*-
from flask import Flask

from apps.apis.news_api import news_bp
from apps.apis.user_api import user_bp
from exts import db, cors, cache
from settings import config

cache_config = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': '127.0.0.1',
    'CACHE_REDIS_PORT': 6379
}

def create_app(config_name):
    app = Flask(__name__, static_folder='../static')
    # 添加app配置
    app.config.from_object(config[config_name])

    # 初始化数据库
    db.init_app(app=app)

    # 添加跨域处理,支持当前证书
    cors.init_app(app=app, supports_crendentials=True)

    # 注册蓝图
    app.register_blueprint(news_bp)
    app.register_blueprint(user_bp)

    # 注册缓存
    cache.init_app(app=app,config=cache_config)

    return app
