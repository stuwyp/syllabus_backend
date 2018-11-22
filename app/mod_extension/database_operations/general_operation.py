# coding = utf-8
import time

from sqlalchemy.exc import IntegrityError, InternalError  # 不是 pymysql.err.IntegrityError

from app import db
from app.models import User, VISIBILITY_VISIBLE


def get_last_inserted_id(model):
    # with_entities(model.field, xxx)    # 仅仅取指定的字段
    return model.query.with_entities(model.id).order_by(model.id.desc()).first().id


def commit():
    try:
        db.session.commit()
        print("commit successful!")
        return True, None
    except Exception as e:
        db.session.rollback()
        print("commit failed", repr(e))
        return False, str(e)


def insert_to_database(model, thing):
    try:
        db.session.add(thing)
        db.session.commit()
        print("insert successful!")
        latest_id = get_last_inserted_id(model)
        return True, latest_id
    except IntegrityError as e:
        db.session.rollback()
        print("insert failed  :", repr(e))
        if "Duplicate" in repr(e):
            return False, "Duplicate entry"
        return False, "Wrong data"
    except InternalError as e:
        db.session.rollback()
        print("insert failed  :", repr(e))
        if "InternalError" in repr(e):
            return False, "Incorrect data format"
        return False, "wrong data"
    except Exception as e:
        db.session.rollback()
        print("insert failed", repr(e))
        return False, "wrong data"


def delete_from_database(thing):
    try:
        db.session.delete(thing)
        db.session.commit()
        print("delete successful!")
        return True, "deleted"

    except Exception as e:
        db.session.rollback()
        print("delete failed", repr(e))
        return False, "wrong operation"


# 一些通用操作
def query_single_by_id(model, id_):
    """
    返回表中主键值为id_的记录
    :param model: 表的模型
    :param id_: 主键
    :return:    记录 或者 None
    """
    if hasattr(model, "visibility"):
        return model.query.filter_by(id=id_).filter_by(visibility=VISIBILITY_VISIBLE).first()
    else:
        return model.query.filter_by(id=id_).first()

    # 参考文档
    # return model.query.get(id_)


def check_token(args):
    uid = args.get("uid")
    token = args.get("token")
    # print(uid, token)
    if uid is None or token is None:
        return False
    if uid is not None and token is not None:
        user = query_single_by_id(User, uid)
        if user is None:
            return False
        print("token for {} is {}".format(user.account, user.token))
        # print("real token {}, input token {}".format(user.token, token))
        if user.token == token:
            # print("token is right")
            return True
        else:
            print("token wrong {}".format(token))
    return False


def is_valid_date(str):
    '''判断是否是一个有效的日期字符串'''
    try:
        time.strptime(str, "%Y-%m-%d")
        return True
    except:
        return False


if __name__ == '__main__':
    print(is_valid_date("2018-2-2 18:18:18"))
