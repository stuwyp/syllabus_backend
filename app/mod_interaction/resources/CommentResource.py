# coding=utf-8
import traceback

from flask_restful.reqparse import RequestParser

from app.mod_interaction.database_operations.comment_operation import get_personal_comment_by_page

__author__ = 'smallfly'

from flask_restful import reqparse, fields, Resource
from app.mod_interaction.resources.GenericSingleResource import GenericSingleResource
from app.mod_interaction.resources.GenericOneToManyRelationResource import GenericOneToManyRelationResource
from app.mod_interaction.database_operations import common
from app.models import Comment

__user_structure = {
    "nickname": fields.String,
    "account": fields.String
}

SINGLE_COMMENT_STRUCTURE = {
    "id": fields.Integer,
    "post_time": fields.String,
    "comment": fields.String,
    "post_id": fields.Integer,
    "uid": fields.Integer,
    "user": fields.Nested(__user_structure)
}

post_parser = reqparse.RequestParser(trim=True)
post_parser.add_argument("post_id", required=True, type=int, location="json")
post_parser.add_argument("uid", required=True, type=int, location="json")
post_parser.add_argument("comment", required=True, location="json")
post_parser.add_argument("token", required=True, location="json")

put_parser = post_parser.copy()
put_parser.add_argument("id", required=True, type=int, location="json")

delete_parser = reqparse.RequestParser(trim=True)
delete_parser.add_argument("uid", required=True, type=int, location="headers")
delete_parser.add_argument("token", required=True, location="headers")
delete_parser.add_argument("id", required=True, type=int, location="headers")

SINGLE_USER_INITIAL_KWARGS = {
    GenericSingleResource.ACCEPTED_VARIABLE_DICT: {
        "put": ["id", "post_id", "uid", "comment", "token"],
        "post": ["post_id", "uid", "comment", "token"],
    },
    GenericSingleResource.MARSHAL_STRUCTURE: SINGLE_COMMENT_STRUCTURE,
    GenericSingleResource.MODEL: Comment,
    GenericSingleResource.RESOURCE_NAME: "comment",
    GenericSingleResource.PARSERS_FOR_METHOD: {
        "post": post_parser,
        "put": put_parser,
        "delete": delete_parser
    },
    GenericSingleResource.TOKEN_CHECK_FOR_METHODS_DICT: {
        "post": common.check_token,
        "put": common.check_token,
        "delete": common.check_token
    }
}

# 查找属于某个post的所有评论

get_comments_parser = reqparse.RequestParser(trim=True)
# 必须参数
# 比较的字段
get_comments_parser.add_argument(common.QUERY_ATTR_FILTER_FIELD, required=True, location="args")
get_comments_parser.add_argument(common.QUERY_ATTR_FILTER_VALUE, required=True, location="args")

# 处理结果的可选参数
get_comments_parser.add_argument(common.QUERY_ATTR_COUNT, type=int, location="args")
get_comments_parser.add_argument(common.QUERY_ATTR_ORDER_BY, location="args")
get_comments_parser.add_argument(common.QUERY_ATTR_SORT_TYPE, type=int, location="args")  # 1 表示升序, 2 表示降序
get_comments_parser.add_argument(common.QUERY_ATTR_BEFORE_ID, type=int, location="args")

QUERY_COMMENTS_FOR_POST_INITIAL_KWARGS = {
    GenericOneToManyRelationResource.PARSER_FOR_METHODS_DICT: {
        "get": get_comments_parser
    },
    GenericOneToManyRelationResource.MARSHAL_STRUCTURE: SINGLE_COMMENT_STRUCTURE,
    GenericOneToManyRelationResource.ENVELOPE: "comments",
    GenericOneToManyRelationResource.MODEL: Comment,
}


class PersonalCommentResource(Resource):
    def __init__(self):
        super(PersonalCommentResource, self).__init__()
        self.get_parser = RequestParser(trim=True)

    def get(self):
        self.get_parser.add_argument("uid", type=int, required=True, location="args")
        self.get_parser.add_argument("token", required=True, location="args")
        # 用于分页
        self.get_parser.add_argument("page_index", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_size", type=int, location="args")
        args = self.get_parser.parse_args()
        # 检查token
        if common.check_token(args):
            # print(args)
            try:
                ret = personal_comments_query(args)

                if ret[0]:
                    return ret[1],200
                return {"error": ret[1]}, 404
            except Exception as e:
                print(traceback.print_exc())
                return {"error": repr(e)}, 500
        else:
            return {"error": "unauthorized"}, 401


def personal_comments_query(arg_dict):

    page_index = arg_dict['page_index'] or 1
    page_size = arg_dict['page_size'] or 10

    page_obj = get_personal_comment_by_page(arg_dict['uid'], page_index, page_size)
    return page_obj
