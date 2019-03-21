# coding=utf-8
import traceback

from flask_restful import fields, Resource, marshal
from flask_restful.reqparse import RequestParser
from app.mod_extension.database_operations import general_operation
from app.mod_extension.database_operations.findlost_operation import *

USER_STRUCTURE = {
    "id": fields.Integer,
    "image": fields.String,
    "nickname": fields.String,
    "account": fields.String
}

SINGLE_FINDLOST_STRUCTURE = {
    "id": fields.Integer,
    "user": fields.Nested(USER_STRUCTURE),
    "title": fields.String,
    "location": fields.String,
    "release_time": fields.String,
    "description": fields.String,
    "contact": fields.String,
    "img_link": fields.String,
    "kind": fields.Integer,
    # "status": fields.String
}


def findlost_query(arg_dict):
    uid = arg_dict.get('uid')
    kind = arg_dict['kind'] if arg_dict['kind'] is not None else -1
    page_index = arg_dict['page_index'] or 1
    page_size = arg_dict['page_size'] or 10

    # 按照发布时间排序
    page_obj = get_findlost_by_page(uid, kind, page_index, page_size)
    return page_obj


class FindLostResource(Resource):
    def __init__(self):
        super(FindLostResource, self).__init__()

        self.structure = SINGLE_FINDLOST_STRUCTURE

        self.post_parser = RequestParser(trim=True)

        self.get_parser = RequestParser(trim=True)

        self.put_parser = RequestParser(trim=True)

        self.delete_parser = RequestParser(trim=True)

    # title, location, description, contact, img_link, kind
    def post(self):
        self.post_parser.add_argument("uid", type=int, required=True, location="form")
        self.post_parser.add_argument("token", required=True, location="form")
        self.post_parser.add_argument("title", required=True, location="form")
        self.post_parser.add_argument("location", required=True, location="form")
        self.post_parser.add_argument("description", required=True, location="form")
        self.post_parser.add_argument("contact", required=True, location="form")
        self.post_parser.add_argument("img_link", required=False, location="form")
        self.post_parser.add_argument("kind", type=int, required=True, location="form")

        args = self.post_parser.parse_args()
        # 检查token
        if general_operation.check_token(args):
            try:
                # uid, title, location, description, contact, img_link, kind)
                ret = findlost_add(args['uid'], args['title'], args['location'],
                                   args['description'], args['contact'], args['img_link'], args['kind'])
                # print(ret)
                if ret[0]:
                    return {"status": "created", 'id': ret[1]}, 200
                else:
                    return {"error": ret[1]}, 400
            except Exception as e:
                print("error : ", repr(e))
                return {"error": "wrong operation"}, 500
        return {"error": "unauthorized"}, 401

    def get(self, id=None):
        if id is None:
            return {"error": "bad request"}, 400

        one = general_operation.query_single_by_id(FindLost, id)
        if one is None:
            return {"error": "invalid id {} for {}".format(id, 'FindLost')}, 404
        print(one)
        return marshal(one, self.structure), 200

    def put(self):
        # uid, title, location,  description, contact, img_link, kind)
        self.put_parser.add_argument("uid", type=int, required=True, location="form")
        self.put_parser.add_argument("token", required=True, location="form")
        self.put_parser.add_argument("findlost_id", type=int, required=True, location="form")
        self.put_parser.add_argument("title", required=True, location="form")
        self.put_parser.add_argument("location", required=True, location="form")
        self.put_parser.add_argument("description", required=True, location="form")
        self.put_parser.add_argument("contact", required=True, location="form")
        self.put_parser.add_argument("img_link", required=False, location="form")
        self.put_parser.add_argument("kind", type=int, required=True, location="form")
        args = self.put_parser.parse_args()

        # 检查token
        if general_operation.check_token(args):
            print(args)
            try:
                ret = findlost_update(args['uid'], args['findlost_id'], args['title'], args['location'],
                                      args['description'], args['contact'], args.get('img_link', ''), args['kind'])
                if ret[0]:
                    return {"status": "updated"}, 200
                else:
                    return {"error": ret[1]}, ret[2]
            except Exception as e:
                print(traceback.print_exc())
                return {"error": "wrong operation"}, 500
        else:
            return {"error": "unauthorized"}, 401

    def delete(self):
        # 头部的key不能有下划线
        self.delete_parser.add_argument("findlostid", type=int, required=True, location="headers")
        self.delete_parser.add_argument("uid", type=int, required=True, location="headers")
        self.delete_parser.add_argument("token", required=True, location="headers")
        args = self.delete_parser.parse_args()

        # 检查token
        if general_operation.check_token(args):
            # print(args)
            try:
                ret = findlost_delete(args['uid'], args['findlostid'])
                if ret[0]:
                    return {"status": "deleted"}, 200
                else:
                    print("error : ", ret[1])
                    return {"error": ret[1]}, ret[2]
            except Exception as e:
                print("error : ", repr(e))
                return {"error": "wrong operation"}, 500
        else:
            return {"error": "unauthorized"}, 401


class FindLostResources(Resource):
    def __init__(self):
        super(FindLostResources, self).__init__()
        self.get_parser = RequestParser(trim=True)

    def get(self):
        self.get_parser.add_argument("uid", type=int, required=True, location="args")
        self.get_parser.add_argument("token", required=True, location="args")
        self.get_parser.add_argument("kind", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_index", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_size", type=int, location="args")
        args = self.get_parser.parse_args()

        # 检查token
        if general_operation.check_token(args):
            # print(args)
            args.pop('uid')
            try:
                ret = findlost_query(args)
                print(ret)
                if ret[0]:
                    return ret[1], 200
                else:
                    return {"error": ret[1]}, 404
            except Exception as e:
                print(traceback.print_exc())
                return {"error": repr(e)}, 500
        else:
            return {"error": "unauthorized"}, 401


class PersonalFindLostResources(Resource):
    def __init__(self):
        super(PersonalFindLostResources, self).__init__()
        self.get_parser = RequestParser(trim=True)

    def get(self):
        self.get_parser.add_argument("uid", type=int, required=True, location="args")
        self.get_parser.add_argument("token", required=True, location="args")
        self.get_parser.add_argument("kind", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_index", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_size", type=int, location="args")
        args = self.get_parser.parse_args()

        # 检查token
        if general_operation.check_token(args):
            # print(args)

            try:
                ret = findlost_query(args)
                print(ret)
                if ret[0]:
                    return ret[1], 200
                else:
                    return {"error": ret[1]}, 404
            except Exception as e:
                print(traceback.print_exc())
                return {"error": repr(e)}, 500
        else:
            return {"error": "unauthorized"}, 401
