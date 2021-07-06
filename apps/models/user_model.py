# -*- coding: utf-8 -*-
from apps.models import BaseModel
from exts import db


class User(BaseModel):
    __tablename__ = 'user'

    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(256))
    phone = db.Column(db.String(11), unique=True, nullable=False)
    icon = db.Column(db.String(256))

    newslist = db.relationship('News', backref='author')
    comments = db.relationship('Comment', backref='user')
    replys = db.relationship('Reply', backref='rep_user')

    def __str__(self):
        return self.username
