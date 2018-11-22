# coding = utf-8
from app import models
from app.mod_extension.database_operations.general_operation import insert_to_database, query_single_by_id, \
    delete_from_database
from app.mod_extension.database_operations.user_operation import get_user_by_id
from app.mod_interaction.database_operations import common
from app.models import CommentThumbUp, Comment


def has_comment_liked(uid, cid):
    """
    检查uid这位用户是否已经给cid的评论点过赞了
    :param uid: 用户
    :param cid: comment
    :return:
    """
    all_likes = common.fetch_all(CommentThumbUp)
    if len(all_likes) == 0:
        # print("empty")
        return False
    else:
        # 检查该用户是否点过赞了
        for like in all_likes:
            if like.uid == uid and cid == like.comment_id:
                return True
    return False

def comment_like_add(uid, comment_id):
    user = get_user_by_id(uid)
    if user is None:
        return False, 404, "user doesn't exist"
    com = query_single_by_id(Comment, comment_id)
    if com is None:
        return False, 404, "comment doesn't exist"
    if has_comment_liked(uid, comment_id):
        return False, 403, "can't like the same comment more than once"
    kwargs = {
        'uid': uid,
        'comment_id': comment_id
    }
    comment = CommentThumbUp(**kwargs)
    user.comment_thumb_ups.append(comment)
    ret = insert_to_database(CommentThumbUp, comment)
    return ret


def comment_like_delete(comment_like_id, uid):
    user = get_user_by_id(uid)
    if user is None:
        return False, 404, "user doesn't exist"
    result = CommentThumbUp.query.filter_by(id=comment_like_id).first()
    if result is None:
        return False, 404, "comment_like_id doesn't exist"
    if uid != result.uid:
        return False, 403, "comment_like_id doesn't match with uid "

    return delete_from_database(result)
