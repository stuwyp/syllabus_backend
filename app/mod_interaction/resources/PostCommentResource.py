# coding=utf-8
import traceback

from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.mod_extension.database_operations import general_operation
from app.mod_interaction.database_operations.post_sort_operation import get_post_by_page, get_personal_post_by_page


def post_query_sort(arg_dict):
    # print(arg_dict)
    topic_id = arg_dict['topic_id'] if arg_dict['topic_id'] is not None else -1
    mode = arg_dict['mode'] or 1
    latest_days = arg_dict['latest_days'] or 3
    page_index = arg_dict['page_index'] or 1
    page_size = arg_dict['page_size'] or 10

    page_obj = get_post_by_page(page_index, page_size, mode,topic_id,latest_days)
    return page_obj


def personal_post_query(arg_dict):
    # print(arg_dict)
    topic_id = arg_dict['topic_id'] if arg_dict['topic_id'] is not None else -1
    page_index = arg_dict['page_index'] or 1
    page_size = arg_dict['page_size'] or 10

    page_obj = get_personal_post_by_page(arg_dict['uid'], page_index, page_size, topic_id)
    return page_obj


class PostSortResource(Resource):

    def __init__(self):
        super(PostSortResource, self).__init__()
        self.get_parser = RequestParser(trim=True)

    def get(self):

        self.get_parser.add_argument("mode", type=int, location="args")
        self.get_parser.add_argument("latest_days", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_index", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_size", type=int, location="args")
        self.get_parser.add_argument("topic_id", type=int, location="args")
        args = self.get_parser.parse_args()

        try:
            ret = post_query_sort(args)
            if ret[0]:
                return ret[1]
            return {"error": ''}, 404
        except Exception as e:
            print(traceback.print_exc())
            return {"error": repr(e)}, 500


class PersonalPostSortResource(Resource):

    def __init__(self):
        super(PersonalPostSortResource, self).__init__()
        self.get_parser = RequestParser(trim=True)

    def get(self):
        self.get_parser.add_argument("uid", type=int, required=True, location="args")
        self.get_parser.add_argument("token", required=True, location="args")
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
                ret = personal_post_query(args)

                if ret[0]:
                    return ret[1]
                return {"error": ''}, 404
            except Exception as e:
                print(traceback.print_exc())
                return {"error": repr(e)}, 500
        else:
            return {"error": "unauthorized"}, 401
