# coding=utf-8
from datetime import datetime

from flask_restful import fields, Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.exc import StatementError

from app.mod_extension.database_operations import general_operation

from app.mod_extension.database_operations.todo_operation import get_todo_by_page, todo_add, todo_update, todo_delete, \
    todo_update_status


def todo_query(arg_dict):
    print(arg_dict)
    mode = arg_dict['mode'] or 1

    page_index = arg_dict['page_index'] or 1
    page_size = arg_dict['page_size'] or 10

    # 按照时间排序
    page_obj = get_todo_by_page(arg_dict['uid'], mode, page_index, page_size)

    return page_obj


class TodoResource(Resource):

    def __init__(self):
        super(TodoResource, self).__init__()

        self.post_parser = RequestParser(trim=True)

        self.get_parser = RequestParser(trim=True)

        self.put_parser = RequestParser(trim=True)

        self.delete_parser = RequestParser(trim=True)

    def post(self):
        self.post_parser.add_argument("uid", type=int, required=True, location="form")
        self.post_parser.add_argument("token", required=True, location="form")
        self.post_parser.add_argument("label", required=True, location="form")
        self.post_parser.add_argument("title", required=True, location="form")
        self.post_parser.add_argument("content", required=True, location="form")
        self.post_parser.add_argument("start_time", required=True, location="form")
        self.post_parser.add_argument("deadline_time", required=True, location="form")
        self.post_parser.add_argument("priority", type=int, required=True, location="form")
        self.post_parser.add_argument("img_link", location="form")

        args = self.post_parser.parse_args()
        start_time = datetime.strptime(args['start_time'], "%Y-%m-%d %H:%M:%S").timestamp()
        deadline_time = datetime.strptime(args['deadline_time'], "%Y-%m-%d %H:%M:%S").timestamp()
        if start_time >= deadline_time:
            return {"error": "deadline_time <= start_time"}, 400
        # 检查token
        if general_operation.check_token(args):

            try:
                ret = todo_add(args['uid'], args['label'], args['title'], args['content'], args['start_time'],
                               args['deadline_time'], args['priority'], 0, args['img_link'])
                print(ret)
                if ret[0]:
                    return {"status": "created", 'id': ret[1]}, 200
                else:
                    return {"error": ret[1]}, 400
            except Exception as e:
                print("error : ", repr(e))
                return {"error": "wrong operation"}, 500
        return {"error": "unauthorized"}, 401

    def get(self):
        self.get_parser.add_argument("uid", type=int, required=True, location="args")
        self.get_parser.add_argument("token", required=True, location="args")
        self.get_parser.add_argument("mode", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_index", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_size", type=int, location="args")
        args = self.get_parser.parse_args()
        # 检查token
        if general_operation.check_token(args):
            print(args)
            try:
                ret = todo_query(args)
                print(ret)
                if ret[0]:
                    return ret[1], 200
                else:
                    return {"error": ret[1]}, 404
            except Exception as e:
                print(repr(e))
                return {"error": repr(e)}, 500
        else:
            return {"error": "unauthorized"}, 401

    def put(self):
        self.put_parser.add_argument("uid", type=int, required=True, location="form")
        self.put_parser.add_argument("token", required=True, location="form")
        self.put_parser.add_argument("todo_id", type=int, required=True, location="form")
        self.put_parser.add_argument("label", required=True, location="form")
        self.put_parser.add_argument("title", required=True, location="form")
        self.put_parser.add_argument("content", required=True, location="form")
        self.put_parser.add_argument("start_time", required=True, location="form")
        self.put_parser.add_argument("deadline_time", required=True, location="form")
        self.put_parser.add_argument("priority", type=int, required=True, location="form")
        self.put_parser.add_argument("img_link", location="form")
        args = self.put_parser.parse_args()
        start_time = datetime.strptime(args['start_time'], "%Y-%m-%d %H:%M:%S").timestamp()
        deadline_time = datetime.strptime(args['deadline_time'], "%Y-%m-%d %H:%M:%S").timestamp()
        if start_time >= deadline_time:
            return {"error": "deadline_time <= start_time"},
        # 检查token
        if general_operation.check_token(args):
            # print(args)
            try:
                ret = todo_update(args['todo_id'], args['label'], args['title'], args['content'], args['start_time'],
                                  args['deadline_time'], args['priority'], 0, args.get('img_link', ''), )
                if ret[0]:
                    return {"status": "updated"}, 200
                else:
                    return {"error": ret[1]}, 404
            except Exception as e:
                return {"error": "wrong operation"}, 500
        else:
            return {"error": "unauthorized"}, 401

    def delete(self):
        # 头部的key不能有下划线
        self.delete_parser.add_argument("todoid", type=int, required=True, location="headers")
        self.delete_parser.add_argument("uid", type=int, required=True, location="headers")
        self.delete_parser.add_argument("token", required=True, location="headers")
        args = self.delete_parser.parse_args()

        # 检查token
        if general_operation.check_token(args):
            # print(args)
            try:
                ret = todo_delete(args['todoid'], args['uid'])
                if ret[0]:
                    return {"status": "deleted"}, 200
                else:
                    print("error : ", ret[1])
                    return {"error": ret[1]}, 404
            except Exception as e:
                print("error : ", repr(e))
                return {"error": "wrong operation"}, 500
        else:
            return {"error": "unauthorized"}, 401


class TodoStatusResource(Resource):

    def __init__(self):
        super(TodoStatusResource, self).__init__()
        self.put_parser = RequestParser(trim=True)

    def put(self):

        self.put_parser.add_argument("todo_id", type=int, required=True, location="form")
        self.put_parser.add_argument("uid", type=int, required=True, location="form")
        self.put_parser.add_argument("token", required=True, location="form")
        self.put_parser.add_argument("status", type=int, required=True, location="form")

        args = self.put_parser.parse_args()

        # 检查token
        if general_operation.check_token(args):
            # print(args)
            try:
                ret = todo_update_status(args['todo_id'], args['status'])
                if ret[0]:
                    return {"status": "updated"}, 200
                else:
                    return {"error": ret[1]}, 404
            except StatementError as e:
                return {"error": "bad request"}, 400
            except Exception as e:
                return {"error": "wrong operation"}, 500
        else:
            return {"error": "unauthorized"}, 401
