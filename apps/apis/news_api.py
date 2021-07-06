# -*- coding: utf-8 -*-
from flask import Blueprint, g
from flask_restful import Api, Resource, fields, marshal_with, reqparse, marshal

from apps.models.news_model import NewsType, News
from apps.util import login_required
from exts import db

news_bp = Blueprint('news', __name__)
api = Api(news_bp)

type_fields = {
    'id': fields.Integer,
    # name提供给前端，attribute是模型中字段名
    'name': fields.String(attribute='type_name')
}

# 添加分类传入
type_parser = reqparse.RequestParser()
type_parser.add_argument('typeName', type=str, required=True,
                         help='必须添加新闻分类名称', location='form')

# 修改分类的传入
update_type_parser = type_parser.copy()
update_type_parser.add_argument('id', type=int, required=True,
                                help='必须添加要修改的分类id', location='form')
# 删除类型传入
delete_type_parser = reqparse.RequestParser()
delete_type_parser.add_argument('id', type=int, required=True,
                                help='必须添加要删除的分类id', location='form')


# 新闻类型的api
class NewsTypeApi(Resource):
    @marshal_with(type_fields)
    def get(self):
        types = NewsType.query.all()
        return types

    def post(self):
        args = type_parser.parse_args()
        type_name = args.get('typeName')
        # 数据库添加
        newsType = NewsType()
        newsType.type_name = type_name
        db.session.add(newsType)
        db.session.commit()
        return marshal(newsType, type_fields)

    # 修改分类名称
    def patch(self):
        args = update_type_parser.parse_args()
        type_id = args.get('id')
        new_type_name = args.get('typeName')
        type_obj = NewsType.query.get(type_id)
        if type_obj:
            type_obj.type_name = new_type_name
            db.session.commit()
            data = {
                'status_code': 200,
                'msg': 'modify successfully',
                'type': marshal(type_obj, type_fields)
            }
        else:
            data = {
                'status_code': 400,
                'msg': 'modify failed, no this type.'
            }
        return data

    # 删除分类名称
    def delete(self):
        args = delete_type_parser.parse_args()
        type_id = args.get('id')
        type_obj = NewsType.query.get(type_id)
        if type_obj:
            # 此处删除被关联的分类会报错
            db.session.delete(type_obj)
            db.session.commit()
            data = {
                'status_code': 200,
                'msg': 'news type delete successfully!'
            }
        else:
            data = {
                'status_code': 400,
                'msg': 'news type delete failed!'
            }
        return data


# 新闻api
news_parser = reqparse.RequestParser()
news_parser.add_argument('typeid', type=int, help='必须添加新闻类型', required=True)
news_parser.add_argument('page', type=int)


# 自定义fields类型
class AuthorName(fields.Raw):
    def format(self, value):
        return value.username


# 输出的每条新闻的格式
news_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'desc': fields.String,
    'datetime': fields.DateTime(attribute='date_time'),
    'author': AuthorName(attribute='author'),
    # 此处endpoint中news为蓝图名
    'url': fields.Url(endpoint='news.newsdetail', absolute=True, scheme='http')
}


class NewsListApi(Resource):
    # 获取某个分类下的新闻
    def get(self):
        args = news_parser.parse_args()
        type_id = args.get('typeid')
        page = args.get('page')
        pagination = News.query.filter(News.news_type_id == type_id).paginate(page=page, per_page=8)
        data = {
            'has_more': pagination.has_next,
            'data': marshal(pagination.items, news_fields),
            'return_count': len(pagination.items),
            'html': 'null'
        }
        return data


# 评论回复
reply_fields = {
    'user': AuthorName(attribute='rep_user'),
    'content': fields.String,
    'datetime': fields.DateTime(attribute='date_time'),
    'loveNum': fields.Integer(attribute='love_num')
}

# 新闻评论
comment_fields = {
    'user': AuthorName(attribute='user'),
    'content': fields.String,
    'datetime': fields.DateTime(attribute='date_time'),
    'loveNum': fields.Integer(attribute='love_num'),
    'replys': fields.List(fields.Nested(reply_fields))
}
# 新闻详情
news_detail_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'content': fields.String,
    'datetime': fields.DateTime(attribute='date_time'),
    'author': AuthorName(attribute='author'),
    'comments': fields.List(fields.Nested(comment_fields))
}


class NewsDetailApi(Resource):
    @marshal_with(news_detail_fields)
    def get(self, id):
        news = News.query.get(id)
        return news


# 定义新闻添加的传入
add_news_parser = reqparse.RequestParser()
add_news_parser.add_argument('title', type=str, required=True,
                             help='新闻标题不能为空', location='form')
add_news_parser.add_argument('content', type=str, required=True,
                             help='新闻主题内容不能为空', location='form')
add_news_parser.add_argument('typeid', type=int, required=True,
                             help='新闻类型不能为空', location='form')


class NewsApi(Resource):
    @login_required
    def post(self):
        args = add_news_parser.parse_args()
        title = args.get('title')
        content = args.get('content')
        type_id = args.get('typeid')
        # 数据库条添加
        news = News()
        news.title = title
        news.content = content
        news.desc = content[:100] + '...'
        news.news_type_id = type_id
        news.user_id = g.user.id
        db.session.add(news)
        db.session.commit()
        data = {
            'status_code': 200,
            'msg': '新闻发布成功',
            'news': marshal(news, news_detail_fields)
        }
        return data

    def patch(self):
        return {'status_code': 400, 'msg': '新闻修改成功'}

    @login_required
    def put(self):
        pass

    @login_required
    def delete(self):
        pass


api.add_resource(NewsTypeApi, '/types')
api.add_resource(NewsListApi, '/newslist')
api.add_resource(NewsDetailApi, '/newsdetail/<int:id>', endpoint='newsdetail')
api.add_resource(NewsApi, '/news')
