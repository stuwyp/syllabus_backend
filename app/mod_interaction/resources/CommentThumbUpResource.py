# coding=utf-8
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.mod_extension.database_operations import general_operation
from app.mod_interaction.database_operations.comment_thumb_up_operation import comment_like_add, comment_like_delete


class CommentThumbUpResource(Resource):
    def __init__(self):
        super(CommentThumbUpResource, self).__init__()

        self.post_parser = RequestParser(trim=True)

        # self.get_parser = RequestParser(trim=True)

        self.delete_parser = RequestParser(trim=True)

    def post(self):
        self.post_parser.add_argument("uid", type=int, required=True, location="form")
        self.post_parser.add_argument("token", required=True, location="form")
        self.post_parser.add_argument("comment_id", type=int, required=True, location="form")
        args = self.post_parser.parse_args()
        # 检查token
        if general_operation.check_token(args):

            try:
                ret = comment_like_add(args['uid'], args['comment_id'])
                print(ret)
                if ret[0]:
                    return {"status": "created", 'id': ret[1]}, 200
                else:
                    return {"error": ret[2]}, ret[1]
            except Exception as e:
                print("error : ", repr(e))
                return {"error": "wrong operation"}, 500
        return {"error": "unauthorized"}, 401

    # def get(self):
    #     self.get_parser.add_argument("uid", type=int, required=True, location="args")
    #     self.get_parser.add_argument("token", required=True, location="args")
    #     args = self.get_parser.parse_args()
    #     # 检查token
    #     if general_operation.check_token(args):
    #         print(args)
    #         try:
    #             ret = []
    #             print(ret)
    #             if ret[0]:
    #                 return ret[1], 200
    #             else:
    #                 return {"error": ret[1]}, 404
    #         except Exception as e:
    #             print(traceback.print_exc())
    #             return {"error": repr(e)}, 500
    #     else:
    #         return {"error": "unauthorized"}, 401

    def delete(self):
        # 头部的key不能有下划线
        self.delete_parser.add_argument("id", type=int, required=True, location="headers")
        self.delete_parser.add_argument("uid", type=int, required=True, location="headers")
        self.delete_parser.add_argument("token", required=True, location="headers")
        args = self.delete_parser.parse_args()

        # 检查token
        if general_operation.check_token(args):
            # print(args)
            try:
                ret = comment_like_delete(args['id'], args['uid'])
                if ret[0]:
                    return {"status": "deleted"}, 200
                else:
                    print("error : ", ret[2])
                    return {"error": ret[2]}, ret[1]
            except Exception as e:
                print("error : ", repr(e))
                return {"error": "wrong operation"}, 500
        else:
            return {"error": "unauthorized"}, 401
