# -*- coding: utf-8 -*-
from datetime import datetime

from exts import db


class BaseModel(db.Model):
    # 下面一行表示不能单独作为一个模型
    __abstract__ = True
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    date_time = db.Column(db.DateTime, default=datetime.now)
