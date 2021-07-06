# -*- coding:utf-8 -*-
import os


class Config:
    SECRET_KEY = 'newssoft'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:123456@127.0.0.1:3306/news'
    DEBUG = True


class Production(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:123456@xxx.xxx.xxx.xxx:3306/news'
    DEBUG = False


config = {
    'default': DevelopmentConfig
}
