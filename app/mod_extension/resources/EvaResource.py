# coding=utf-8
from datetime import datetime

from flask_restful import fields, Resource
from flask_restful.reqparse import RequestParser

from app.mod_extension.database_operations import general_operation

from app.mod_extension.database_operations.eva_operation import *


def eva_query(arg_dict):
    # print( arg_dict)
    mode = arg_dict['mode'] or 1
    page_index = arg_dict['page_index'] or 1
    page_size = arg_dict['page_size'] or 10

    # 按照时间排序
    page_obj = get_personal_eva_by_uid(arg_dict['uid'], mode, page_index, page_size)

    return page_obj


def class_eva_query(arg_dict):
    # print(arg_dict)
    teacher_id = arg_dict['teacher_id']
    course_id = arg_dict['course_id']
    class_id = arg_dict['class_id']
    mode = arg_dict['mode'] or 1
    term = arg_dict['term'] or 1
    print("***************************************\nterm : ",term)
    page_index = arg_dict['page_index'] or 1
    page_size = arg_dict['page_size'] or 10

    # 按照时间排序
    page_obj = get_class_eva(teacher_id, course_id,class_id, mode, term,page_index, page_size)

    return page_obj


class EvaluationResource(Resource):

    def __init__(self):
        super(EvaluationResource, self).__init__()

        self.post_parser = RequestParser(trim=True)

        self.get_parser = RequestParser(trim=True)

        self.put_parser = RequestParser(trim=True)

        self.delete_parser = RequestParser(trim=True)

    def post(self):
        self.post_parser.add_argument("uid", type=int, required=True, location="form")
        self.post_parser.add_argument("token", required=True, location="form")
        self.post_parser.add_argument("class_id", type=int, required=True, location="form")
        self.post_parser.add_argument("score", type=int, required=True, location="form")
        self.post_parser.add_argument("tags", required=True, location="form")
        self.post_parser.add_argument("content", required=True, location="form")

        args = self.post_parser.parse_args()

        # 检查token
        if general_operation.check_token(args):
            print(args)
            try:
                # 检测class_id 是否存在
                class_res = get_class_by_class_id(args['class_id'])
                if class_res is None:
                    return {"error": "class_id doesn't exist"}, 404

                teacher_id = class_res.teacher_id
                cid = class_res.cid

                ret = insert_eva(args['uid'], args['class_id'], args['content'], args['tags'], args['score'],
                                 True, cid, teacher_id)

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

            try:

                ret = eva_query(args)

                if ret[0]:
                    return ret[1], 200
                else:
                    return {"error": ret[1]}, 400
            except Exception as e:
                print(repr(e))
                return {"error": "wrong operation"}, 500

        return {"error": "unauthorized"}, 401

    def put(self):
        self.put_parser.add_argument("uid", type=int, required=True, location="form")
        self.put_parser.add_argument("token", required=True, location="form")
        self.put_parser.add_argument("eva_id", type=int, required=True, location="form")
        self.put_parser.add_argument("score", required=True, location="form")
        self.put_parser.add_argument("tags", required=True, location="form")
        self.put_parser.add_argument("content", required=True, location="form")
        args = self.put_parser.parse_args()

        # 检查token
        if general_operation.check_token(args):
            print(args)
            try:
                eva_res = get_eva_by_id(args['eva_id']).first()
                if eva_res is None:
                    return {"error": "eva_id doesn't exist"}, 404
                elif eva_res.uid != args['uid']:
                    return {"error": "eva_id doesn't belong to uid"}, 403
                comment_time = datetime.now()
                ret = update_eva(args['eva_id'], args['content'], args['tags'], args['score'], True,
                                 comment_time)
                if ret[0]:
                    return {"status": "updated"}, 200
                else:
                    return {"error": ret[1]}, 400
            except Exception as e:
                return {"error": "wrong operation"}, 500
        return {"error": "unauthorized"}, 401

    def delete(self):
        # 头部的key不能有下划线
        self.delete_parser.add_argument("evaid", type=int, required=True, location="headers")
        self.delete_parser.add_argument("uid", type=int, required=True, location="headers")
        self.delete_parser.add_argument("token", required=True, location="headers")
        args = self.delete_parser.parse_args()

        # 检查token
        if general_operation.check_token(args):
            print(args)
            try:
                eva_res = get_eva_by_id(args['evaid']).first()
                if eva_res is None:
                    return {"error": "eva_id doesn't exist"}, 404
                elif eva_res.uid != args['uid']:
                    return {"error": "eva_id doesn't belong to uid"}, 403

                ret = delete_eva_by_id(args['evaid'])
                if ret[0]:
                    return {"status": "deleted"}, 200
                else:
                    print("error : ", ret[1])
                    return {"error": ret[1]}, 400
            except Exception as e:
                print("error : ", repr(e))
                return {"error": "wrong operation"}, 500
        return {"error": "unauthorized"}, 401


class ClassEvaluationResource(Resource):

    def __init__(self):
        super(ClassEvaluationResource, self).__init__()

        self.get_parser = RequestParser(trim=True)

    def get(self):

        self.get_parser.add_argument("uid", type=int, required=True, location="args")
        self.get_parser.add_argument("token", required=True, location="args")
        self.get_parser.add_argument("class_id", required=True, location="args")
        self.get_parser.add_argument("mode", type=int, location="args")
        # term = 1：本学期
        # term = -1：所有学期
        self.get_parser.add_argument("term", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_index", type=int, location="args")
        # 用于分页
        self.get_parser.add_argument("page_size", type=int, location="args")
        args = self.get_parser.parse_args()
        # 检查token
        if general_operation.check_token(args):

            try:
                # 检测class_id 是否存在
                class_res = get_class_by_class_id(args['class_id'])
                if class_res is None:
                    return {"error": "class_id doesn't exist"}, 404

                teacher_id = class_res.teacher_id
                cid = class_res.cid

                args['teacher_id'] = teacher_id
                args['course_id'] = cid
                ret = class_eva_query(args)

                if ret[0]:
                    return ret[1], 200
                else:
                    return {"error": ret[1]}, 400
            except Exception as e:
                print(repr(e))
                return {"error": "wrong operation"}, 500

        return {"error": "unauthorized"}, 401
