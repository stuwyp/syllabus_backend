# coding=utf-8
from pprint import pprint

__author__ = 'smallfly'

# 转发到学校服务器进行课表查询

from flask_restful import Resource, reqparse
from app.mod_interaction.database_operations import common
from app import db

from app.models import User
import requests
import requests.exceptions

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
}

parser = reqparse.RequestParser(trim=True)

parser.add_argument("username", required=True, location="form")
parser.add_argument("password", required=True, location="form")
parser.add_argument("years", required=True, location="form")
parser.add_argument("semester", required=True, location="form")
parser.add_argument('Cookie', location='headers')


def new_or_update_user(account, token):
    """
    插入新的用户, 或者是更新旧用户
    :param account:
    :param token:
    :return:
    """
    user = common.query_single_by_field(User, "account", account)
    if user is None:
        # 新用户
        user = User(account=account, token=token)
        ret_val = common.add_to_db(db, user)
        if ret_val != True:
            print(ret_val[1])
            return False
        else:
            return user
    # 老用户
    user.token = token  # 更新token
    ret_val = common.add_to_db(db, user)
    if ret_val != True:
        print(ret_val[1])
        return False
    else:
        return user


class SyllabusResource(Resource):
    SYLLABUS_API_URL = "http://127.0.0.1:8080/syllabus"

    def get(self):
        return {"error": "method not allowed"}, 405

    def post(self):
        args = parser.parse_args()
        if args.get('Cookie',None) is not None:
            HEADERS['Cookie'] = args['Cookie']
            args.pop('Cookie')
        try:
            resp = requests.post(SyllabusResource.SYLLABUS_API_URL, headers=HEADERS, data=args)
            result = resp.json()
            if "token" in result:
                ret = new_or_update_user(args["username"], result["token"])
                if ret != False:
                    # 添加 user_id 到 result 里面
                    result["user_id"] = ret.id
                    result["avatar"] = ret.image
                    result["nickname"] = ret.nickname
                    # 用户等级
                    result["level"] = ret.level
            elif "ERROR" in result:
                # 表明出错了
                return result, resp.status_code
            if 'Cookie' in resp.headers.keys():
                return result, 200, {'Cookie': resp.headers['Cookie']}
            else:
                return result, 200
        except requests.exceptions.ConnectionError:
            # 校内服务器错误
            return {"error": "connection refused"}, 521
