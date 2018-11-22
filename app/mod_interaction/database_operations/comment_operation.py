# coding=utf-8

from flask_restful import marshal, fields

from app.mod_extension.database_operations.user_operation import get_user_by_id

from app.models import Comment, Post

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


def get_personal_comment_by_page(uid, page_index, page_size):
    user = get_user_by_id(uid)
    # print(user)
    if user is None:
        return False, "user doesn't exist"
    # personal_comment_list = [ marshal(item, marshal_structure) for item in user.comments if item.visibility == 1 ]
    # personal_comment_list.reverse()
    # ret = personal_comment_list

    personal_comment_sort_obj = Comment.query.join(Post).filter(Post.visibility == 1  ,Comment.visibility == 1, Comment.uid == uid).order_by(Comment.post_time.desc())

    personal_comment_sort_list = personal_comment_sort_obj.paginate(page_index, page_size, False)

    marshal_structure = SINGLE_COMMENT_STRUCTURE.copy()
    ret = marshal(personal_comment_sort_list.items, marshal_structure)
    print(ret)
    pagination = {'limit': len(ret), 'total': len(personal_comment_sort_obj.all())}
    return True, {'data': ret, 'pagination': pagination}


# get_personal_comment_by_page(1, 1, 10, 1)
