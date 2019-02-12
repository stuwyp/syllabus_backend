# coding=utf-8
import datetime

from flask_restful import marshal
from sqlalchemy import func

from app import db
from app.mod_extension.database_operations.user_operation import get_user_by_id
from app.mod_interaction.resources.PostResource import SINGLE_POST_STRUCTURE
from app.models import Comment, Post, ThumbUp, User, VISIBILITY_INVISIBLE, VISIBILITY_VISIBLE


def anonymous_query(arg_dict):
    print(arg_dict)
    topic_id = arg_dict['topic_id'] if arg_dict['topic_id'] is not None else -1
    mode = arg_dict['mode'] or 1
    page_index = arg_dict['page_index'] or 1
    page_size = arg_dict['page_size'] or 10
    latest_days = arg_dict['latest_days'] or 3
    days_ago = (datetime.datetime.now() - datetime.timedelta(days=latest_days))
    # mode = 1 : 按时间排序（降序）
    # mode = 2 : 按评论数排序（降序）
    # mode = 3 : 按点赞数排序（降序）
    if mode == 1:
        if topic_id == -1:
            post_sort_obj = Post.query.filter(Post.visibility == 1, Post.post_type == 3).order_by(Post.post_time.desc())
        else:
            post_sort_obj = Post.query.filter(Post.visibility == 1, Post.post_type == 3,
                                              Post.topic_id == topic_id).order_by(
                Post.post_time.desc())
        post_sort_list = post_sort_obj.paginate(page_index, page_size, False)


    elif mode == 2:
        # Important
        # with_entities(XXX) 代替 db.session.query(XXX)
        comment_sub = Comment.query.filter(Comment.visibility == VISIBILITY_VISIBLE).with_entities(
            Comment.post_id, func.count(Comment.post_id).label('count')).group_by(
            Comment.post_id).subquery()
        # outerjoin 并集 （不能用join 交集）
        if topic_id == -1:
            post_sort_obj = Post.query.with_entities(Post).filter(Post.visibility == VISIBILITY_VISIBLE).filter(
                Post.post_type == 3).outerjoin(comment_sub).filter(
                Post.post_time > days_ago).order_by(comment_sub.c.count.desc())
        else:
            post_sort_obj = Post.query.with_entities(Post).filter(Post.visibility == VISIBILITY_VISIBLE).filter(
                Post.post_type == 3).filter(Post.topic_id == topic_id).outerjoin(comment_sub).filter(
                Post.post_time > days_ago).order_by(
                comment_sub.c.count.desc())
        post_sort_list = post_sort_obj.paginate(page_index, page_size, False)

    elif mode == 3:
        thumb_sub = ThumbUp.query.with_entities(ThumbUp.post_id, func.count(ThumbUp.post_id).label('count')).group_by(
            ThumbUp.post_id).subquery()
        # outerjoin 并集 （不能用join 交集）
        if topic_id == -1:

            post_sort_obj = Post.query.with_entities(Post).filter(Post.visibility == VISIBILITY_VISIBLE).filter(
                Post.post_type == 3).outerjoin(thumb_sub).filter(
                Post.post_time > days_ago).order_by(thumb_sub.c.count.desc())
        else:
            post_sort_obj = Post.query.with_entities(Post).filter(Post.visibility == VISIBILITY_VISIBLE).filter(
                Post.post_type == 3).filter(Post.topic_id == topic_id).outerjoin(thumb_sub).filter(
                Post.post_time > days_ago).order_by(
                thumb_sub.c.count.desc())
        post_sort_list = post_sort_obj.paginate(page_index, page_size, False)
    else:
        return False, {'error': 'wrong params'}

    marshal_structure = SINGLE_POST_STRUCTURE.copy()
    ret = marshal(post_sort_list.items, marshal_structure)

    pagination = {'limit': len(ret), 'total': len(post_sort_obj.all())}
    return True, {'data': ret, 'pagination': pagination}


def personal_anonymous_query(arg_dict):
    print(arg_dict)
    uid = arg_dict['uid']
    topic_id = arg_dict['topic_id'] if arg_dict['topic_id'] is not None else -1
    page_index = arg_dict['page_index'] or 1
    page_size = arg_dict['page_size'] or 10

    if topic_id == -1:
        personal_anonymous_sort_obj = Post.query.filter(Post.visibility == 1, Post.post_type == 3,
                                                        Post.real_uid == uid).order_by(Post.post_time.desc())
    else:
        personal_anonymous_sort_obj = Post.query.filter(Post.visibility == 1, Post.post_type == 3, Post.real_uid == uid,
                                                        Post.topic_id == topic_id).order_by(Post.post_time.desc())

    personal_anonymous_sort_list = personal_anonymous_sort_obj.paginate(page_index, page_size, False)

    marshal_structure = SINGLE_POST_STRUCTURE.copy()
    ret = marshal(personal_anonymous_sort_list.items, marshal_structure)

    pagination = {'limit': len(ret), 'total': len(personal_anonymous_sort_obj.all())}
    return True, {'data': ret, 'pagination': pagination}


def anonymous_delete(arg_dict):
    uid = arg_dict['uid']
    pid = arg_dict['id']
    user = get_user_by_id(uid)
    if user is None:
        return False, 404, "user doesn't exist"
    result = Post.query.filter_by(id=pid, visibility=VISIBILITY_VISIBLE).first()

    if result is None:
        return False, 404, "anonymous post id doesn't exist"

    super_users = User.query.with_entities(User.id).filter_by(level=User.LEVEL_MANAGER).all()
    super_ids = [user.id for user in super_users]
    if result.real_uid != uid and uid not in super_ids:
        return False, 403, "anonymous post id doesn't match with uid "
    result.visibility = VISIBILITY_INVISIBLE
    db.session.add(result)
    db.session.commit()
    return True, {"status": "deleted"}
