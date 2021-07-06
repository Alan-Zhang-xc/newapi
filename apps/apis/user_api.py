# -*- coding: utf-8 -*-
import random
import uuid

from flask import Blueprint, jsonify, session, request
from flask_restful import Api, Resource, reqparse, inputs, fields, marshal
from werkzeug.security import generate_password_hash, check_password_hash

from apps.models.user_model import User
from apps.util.sendshortmessage import send_shortmsg
from exts import cache, db

user_bp = Blueprint('user', __name__)

api = Api(user_bp)

# 手机验证码类视图
sms_parse = reqparse.RequestParser()
sms_parse.add_argument('mobile', type=inputs.regex(r'^1[3458]\d{9}$'),
                       required=True, location=['form', 'args'], help='手机号码格式有误')


class SendMessageApi(Resource):
    def post(self):
        args = sms_parse.parse_args()
        mobile = args.get('mobile')
        # 短信验证码接口，暂未实现
        ret, code = send_shortmsg(mobile)
        print(ret, code)
        # 验证是否发送成功
        if ret is not None:
            if ret["status_code"] == 200:
                cache.set(mobile, code, timeout=300)
                return jsonify(status_code=200, msg='短信发送成功')
        else:
            return jsonify(status_code=400, msg='获取验证码失败')


# 用户登录和注册
# 输入
lr_parser = sms_parse.copy()
lr_parser.add_argument('code', type=inputs.regex(r'^\d{4}$'), help='验证码格式有误', required=True)

# 输出
user_fields = {
    'id': fields.Integer,
    'username': fields.String
}


class LoginAndRegisterApi(Resource):
    def post(self):
        args = lr_parser.parse_args()
        mobile = args.get('mobile')
        code = args.get('code')
        cache_code = cache.get(mobile)
        if cache_code and cache_code == code:
            # 数据库中查找是否存在此mobile
            user = User.query.filter(User.phone == mobile).first()
            # 判断列表中是否存在用户
            if not user:
                # 跳转注册处理
                user = User()
                user.phone = mobile
                s = ''
                for i in range(13):
                    ran = random.randint(0, 9)
                    s += str(ran)
                user.username = '用户' + s
                db.session.add(user)
                db.session.commit()
            # 登录处理,记录登录状态：session，cookie，cache（redis），token，jwt
            # uuid示例 asddfj-asdnfjkahsdg23sadf-asddfajjkabsdf9-asdfh
            new_token = str(uuid.uuid4()).replace("-", "") + str(random.randint(1000, 9999))
            print(new_token)
            # 存储用户的登录信息
            cache.set(new_token, mobile, timeout=7 * 24 * 60 * 60)

            return {"status_code": 200, "msg": "登录登陆成功", 'new_token': new_token}
        else:
            return {'errmsg': '验证码错误', 'status': 400}


# 忘记密码
class ForgetPasswordApi(Resource):
    def get(self):
        s = 'abcdefghijklmnopqtstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        code = ''
        for i in range(4):
            c = random.choice(s)
            code += c
        # 保存code,此处不能用cache是因为还没有输入手机号
        session['vf_code'] = code
        return {"code": code}


# 申请重置密码的输入
reset_parser = sms_parse.copy()
reset_parser.add_argument('imageCode', type=inputs.regex(r'^[a-zA-Z0-9]{4}$'), help='验证码格式有误', required=True)


class ResetPasswordApi(Resource):
    def get(self):
        args = reset_parser.parse_args()
        mobile = args.get('mobile')
        image_code = args.get('imageCode')
        vf_code = session.get('vf_code')
        if vf_code and image_code.lower() == vf_code.lower():
            # 判断手机号的用户
            print(mobile)
            user = User.query.filter(User.phone == mobile).first()
            print(user)
            if user:
                # 发送短信验证码
                # request()
                ret, sms_code = send_shortmsg(mobile)
                print('短信验证码：', sms_code)
                if ret is not None:
                    if ret["status_code"] == 200:
                        cache.set(mobile, sms_code, timeout=300)
                        return jsonify(status_code=200, msg='短信发送成功')
                else:
                    return jsonify(status_code=400, msg='获取验证码失败')
            else:
                return {'status': 400, 'msg': '此号码未注册'}
        else:
            return {'status': 400, 'msg': '验证码失效，请重试'}


# 更新密码的参数
update_parser = lr_parser.copy()
update_parser.add_argument('password', type=inputs.regex(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])[a-zA-Z0-9]{8,10}$'),
                           help='必须包含大小写字母和数字的组合，不能使用特殊字符，长度在 8-10 之间',
                           required=True, location='form')
update_parser.add_argument('repassword', type=inputs.regex(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])[a-zA-Z0-9]{8,10}$'),
                           help='必须包含大小写字母和数字的组合，不能使用特殊字符，长度在 8-10 之间',
                           required=True, location='form')

# 账户密码登录时前端需要传入的内容
password_login_parser = sms_parse.copy()
password_login_parser.add_argument('password', type=str, required=True, help='必须输入密码')


class UserApi(Resource):
    def post(self):
        args = password_login_parser.parse_args()
        mobile = args.get("mobile")
        password = args.get("password")
        user = User.query.filter(User.phone == mobile).first()
        if user:
            if check_password_hash(user.password, password):
                # uuid示例 asddfj-asdnfjkahsdg23sadf-asddfajjkabsdf9-asdfh
                new_token = str(uuid.uuid4()).replace("-", "") + str(random.randint(1000, 9999))
                print(new_token)
                # cache.set(mobile + "_", 1)
                # 存储用户的登录信息
                cache.set(new_token, mobile, timeout=7 * 24 * 60 * 60)

                return {"status_code": 200, "msg": "登录登陆成功", 'new_token': new_token}
        return {"status_code": 400, "msg": "用户名或密码错误"}

    def put(self):
        args = update_parser.parse_args()
        code = args.get('code')
        mobile = args.get('mobile')
        cache_code = cache.get(mobile)
        # 判断验证码是否正确
        if cache_code and cache_code == code:
            user = User.query.filter(User.phone == mobile).first()
            password = args.get('password')
            repassword = args.get('repassword')
            # 判断密码是否一致
            if password == repassword:
                user.password = generate_password_hash(password)
                db.session.commit()
                return {'status_code': 200, 'msg': '修改密码成功'}
            else:
                return {'status_code': 400, 'msg': '两次密码不一致'}
        else:
            return {'status_code': 200, 'msg': '验证码错误'}


# 发送手机验证码路由
api.add_resource(SendMessageApi, '/sms')
api.add_resource(LoginAndRegisterApi, '/codelogin')
api.add_resource(ForgetPasswordApi, '/forget_pw')
api.add_resource(ResetPasswordApi, '/reset')
api.add_resource(UserApi, '/user')
