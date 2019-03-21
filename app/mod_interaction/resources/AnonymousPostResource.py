# coding=utf-8
import traceback

from app.mod_extension.database_operations import general_operation
from app.mod_interaction.database_operations.anonymous_operation import anonymous_query, personal_anonymous_query, \
    anonymous_delete

__author__ = 'xiaofud'

from flask_restful import Resource, reqparse
from app.models import Post
from app.mod_interaction.database_operations import common
from app import db


class AnonymousResource(Resource):
    """
    发布匿名消息，全部归结为user id为-1的固定用户
    """

    USER_ID = -1
    POST_TYPE = Post.POST_TYPE_ANONYMOUS

    post_parser = reqparse.RequestParser(trim=True)
    get_parser = reqparse.RequestParser(trim=True)
    delete_parser = reqparse.RequestParser(trim=True)

    def post(self):
        self.post_parser.add_argument("source", location="json")
        self.post_parser.add_argument("content", required=True, location="json")
        # self.post_parser.add_argument("uid", type=int, required=True, location="json")
        # self.post_parser.add_argument("post_type", type=int, required=True, location="json")
        # self.post_parser.add_argument("token", required=True, location="json")
        self.post_parser.add_argument("description", location="json")
        self.post_parser.add_argument("photo_list_json", location="json")
        self.post_parser.add_argument("real_uid", type=int, location="json")
        self.post_parser.add_argument("title", location="json")
        self.post_parser.add_argument("topic_id", type=int, location="json")
        args = self.post_parser.parse_args()
        # 添加一些固定的值
        args["uid"] = AnonymousResource.USER_ID
        args["post_type"] = AnonymousResource.POST_TYPE
        result = common.new_record(db, Post, **args)
        if result:
            return {"id": result}, 201  # created
        else:
            return {"error": "failed"}, 400

    def delete(self):

        self.delete_parser.add_argument("uid", type=int, required=True, location="headers")
        self.delete_parser.add_argument("token", required=True, location="headers")
        self.delete_parser.add_argument("id", type=int, required=True, location="headers")

        args = self.delete_parser.parse_args()
        # 检查token
        if general_operation.check_token(args):
            print(args)
            try:
                ret = anonymous_delete(args)
                if ret[0]:
                    return ret[1],200
                return {"error": ret[2]}, ret[1]
            except Exception as e:
                print(traceback.print_exc())
                return {"error": repr(e)}, 500
        else:
            return {"error": "unauthorized"}, 401

    def get(self):

        self.get_parser.add_argument("mode", type=int, location="args")
        self.get_parser.add_argument("latest_days", type=int, location="args")
        self.get_parser.add_argument("topic_id", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_index", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_size", type=int, location="args")
        args = self.get_parser.parse_args()

        # print(args)
        try:
            ret = anonymous_query(args)
            if ret[0]:
                return ret[1],200
            return {"error": ret[1]}, 404
        except Exception as e:
            print(traceback.print_exc())
            return {"error": repr(e)}, 500



class PersonalAnonymousResource(Resource):
    get_parser = reqparse.RequestParser(trim=True)

    def get(self):
        self.get_parser.add_argument("uid", type=int, required=True, location="args")
        self.get_parser.add_argument("token", required=True, location="args")
        self.get_parser.add_argument("mode", type=int, location="args")
        self.get_parser.add_argument("topic_id", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_index", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_size", type=int, location="args")
        args = self.get_parser.parse_args()
        # 检查token
        if general_operation.check_token(args):
            # print(args)
            try:
                ret = personal_anonymous_query(args)
                if ret[0]:
                    return ret[1],200
                return {"error": ret[1]}, 404
            except Exception as e:
                print(traceback.print_exc())
                return {"error": repr(e)}, 500
        else:
            return {"error": "unauthorized"}, 401
