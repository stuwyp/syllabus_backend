# coding=utf-8
__author__ = 'smallfly'

from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.mod_interaction.database_operations import common
from app import db, models


def delete_record(db, record):
    try:
        # 删除数据
        db.session.delete(record)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False, e

def check_token(user, token):
    token_check = {
            "uid": user.id,
            "token": token
    }
    return common.check_token(token_check)


class SyllabusCollectionResource(Resource):
    """
    用于记录课表
    """

    POST_PARSER = RequestParser(trim=True)
    GET_PARSER = RequestParser(trim=True)
    DELETE_PARSER = RequestParser(trim=True)

    def get(self):
        """
        申请人获取用户已经上传的课表数据
        地址: /interaction/api/v2/syllabus_collection
        方法: GET
        参数:
            位置: headers
            必须参数:
                username 用户账号
                token 验证令牌
                collectionID 之前申请到的获取id
        :return:
        """
        self.GET_PARSER.add_argument("username", required=True, location="headers")
        self.GET_PARSER.add_argument("token", required=True, location="headers")
        # header里面的键名不能有下划线
        self.GET_PARSER.add_argument("collectionID", required=True, location="headers")

        args = self.GET_PARSER.parse_args()
        user = common.query_single_by_field(models.User, "account", args["username"])
        if user is None:
            return {"error": "user doesn't exist"}, 404

        if not check_token(user, args["token"]):
            return {"error": "token is wrong"}, 401

        collector = common.query_single_by_field(models.Collector, "collection_id", args["collectionID"])
        if collector is None:
            # 表明用户输入了错误的collection_id
            return {"error": "wrong collection_id"}, 404

        # 检查权限
        if collector.uid != user.id:
            return {"error": "have not the permission"}, 403

        collections = models.SyllabusCollection.query.filter_by(collection_id=args["collectionID"]).all()
        collections = [ dict(id=x.id, account=x.account, syllabus=x.syllabus) for x in collections ]
        return {"collections": collections}


    def post(self):
        """
        发送课表数据到服务器
        地址: /interaction/api/v2/syllabus_collection
        方法: POST
        参数:
            位置: form
            必选参数:
                username 用户账号
                token 验证令牌
                start_year 学年的开始年份
                season 某个学期, 和学分制对应
                syllabus 课表的JSON数据
        :return:
        """
        self.POST_PARSER.add_argument("username", required=True, location="form")
        self.POST_PARSER.add_argument("token", required=True, location="form")
        self.POST_PARSER.add_argument("start_year", type=int, required=True, location="form")
        self.POST_PARSER.add_argument("season", type=int, required=True, location="form")
        self.POST_PARSER.add_argument("collection_id", required=True, location="form")
        self.POST_PARSER.add_argument("syllabus", required=True, location="form")

        args = self.POST_PARSER.parse_args()
        user = common.query_single_by_field(models.User, "account", args["username"])
        if user is None:
            return {"error": "user doesn't exist"}, 404

        if not check_token(user, args["token"]):
            return {"error": "token is wrong"}, 401

        collector = common.query_single_by_field(models.Collector, "collection_id", args["collection_id"])
        if collector is None:
            # 表明用户输入了错误的collection_id
            return {"error": "wrong collection_id"}, 404

        # 检查学期是否正确
        if collector.start_year != args["start_year"] or collector.season != args["season"]:
            return {"error": "semester doesn't match"}, 400

        collection = models.SyllabusCollection.query.filter_by(account=user.account).filter_by(collection_id=args["collection_id"]).first()

        if collection is not None:
            # 删除原有记录
            status = delete_record(db, collection)
            if status != True:
                return {"error": repr(status[1])}, 500

        collection = models.SyllabusCollection(collection_id=args["collection_id"], syllabus=args["syllabus"], account=args["username"])

        result = common.add_to_db(db, collection)
        if result == True:
            return {"id": collection.id}
        else:
            return {"error": "commit error in mysql"}, 500


    def delete(self):
        self.DELETE_PARSER.add_argument("username", required=True, location="headers")
        self.DELETE_PARSER.add_argument("token", required=True, location="headers")
        self.DELETE_PARSER.add_argument("id", required=True, location="headers")

        args = self.DELETE_PARSER.parse_args()
        # 检查token
        user = common.query_single_by_field(models.User, "account", args["username"])
        if user is None:
            return {"error": "user doesn't exist"}, 404

        if not check_token(user, args["token"]):
            return {"error": "token is wrong"}, 401

        collection = common.query_single_by_id(models.SyllabusCollection, args["id"])
        if collection is None:
            return {"error": "collection not found"}, 404

        if collection.account == args["username"]:
            status = delete_record(db, collection)
            if status == True:
                return {"status": "deleted"}
            else:
                return {"error": repr(status[1])}, 500
        else:
            collector = common.query_single_by_field(models.Collector, "collection_id", collection.collection_id)
            if collector is None:
                return {"error": "collector not found"}, 404
            if collector.uid == user.id:
                status = delete_record(db, collection)
                if status == True:
                    return {"status": "deleted"}
                else:
                    return {"error": repr(status[1])}, 500
            else:
                return {"error": "have not the permission"}, 403