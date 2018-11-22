# coding=utf-8
import datetime

from flask_restful import marshal
from sqlalchemy import func

from app import models
from app.mod_interaction.resources.PostResource import SINGLE_POST_STRUCTURE
from app.mod_extension.database_operations.user_operation import get_user_by_id
from app.models import Post, Comment, ThumbUp


def get_post_by_page(page_index, page_size, mode, topic_id, latest_days):
    # mode = 1 : 按时间排序（降序）
    # mode = 2 : 按评论数排序（降序）
    # mode = 3 : 按点赞数排序（降序）
    days_ago = (datetime.datetime.now() - datetime.timedelta(days=latest_days))
    if mode == 1:

        if topic_id == -1:
            post_sort_obj = Post.query.filter(Post.visibility == 1, Post.post_type != 2).order_by(Post.post_time.desc())
        else:
            post_sort_obj = Post.query.filter(Post.visibility == 1, Post.post_type != 2,
                                              Post.topic_id == topic_id).order_by(Post.post_time.desc())

        post_sort_list = post_sort_obj.paginate(page_index, page_size, False)

    elif mode == 2:

        # Important
        # with_entities(XXX) 代替 db.session.query(XXX)
        comment_sub = Comment.query.filter(Comment.visibility == models.VISIBILITY_VISIBLE).with_entities(
            Comment.post_id, func.count(Comment.post_id).label('count')).group_by(
            Comment.post_id).subquery()
        # outerjoin 并集 （不能用join 交集）
        if topic_id == -1:
            post_sort_obj = Post.query.with_entities(Post).filter(Post.visibility == models.VISIBILITY_VISIBLE).filter(
                Post.post_type != 2).outerjoin(comment_sub).filter(Post.post_time > days_ago).order_by(
                comment_sub.c.count.desc())

        else:
            post_sort_obj = Post.query.with_entities(Post).filter(Post.visibility == models.VISIBILITY_VISIBLE).filter(
                Post.post_type != 2).filter(Post.topic_id == topic_id).outerjoin(comment_sub).filter(
                Post.post_time > days_ago).order_by(
                comment_sub.c.count.desc())
        post_sort_list = post_sort_obj.paginate(page_index, page_size, False)

    elif mode == 3:

        thumb_sub = ThumbUp.query.with_entities(ThumbUp.post_id, func.count(ThumbUp.post_id).label('count')).group_by(
            ThumbUp.post_id).subquery()
        # outerjoin 并集 （不能用join 交集）
        if topic_id == -1:

            post_sort_obj = Post.query.with_entities(Post).filter(Post.visibility == models.VISIBILITY_VISIBLE).filter(
                Post.post_type != 2).outerjoin(thumb_sub).filter(Post.post_time > days_ago).order_by(
                thumb_sub.c.count.desc())
        else:
            post_sort_obj = Post.query.with_entities(Post).filter(Post.visibility == models.VISIBILITY_VISIBLE).filter(
                Post.post_type != 2).filter(Post.topic_id == topic_id).outerjoin(thumb_sub).filter(
                Post.post_time > days_ago).order_by(thumb_sub.c.count.desc())
        post_sort_list = post_sort_obj.paginate(page_index, page_size, False)


    else:
        return False, {'error': 'wrong params'}

    marshal_structure = SINGLE_POST_STRUCTURE.copy()
    ret = marshal(post_sort_list.items, marshal_structure)
    pagination = {'limit': len(ret), 'total': len(post_sort_obj.all())}

    return True, {'data': ret, 'pagination': pagination}


def get_personal_post_by_page(uid, page_index, page_size, topic_id):
    user = get_user_by_id(uid)
    print(user)
    if user is None:
        return False, "user doesn't exist"
    # personal_post_list = [marshal(item, marshal_structure) for item in user.posts if
    #                       item.visibility == 1 and item.post_type != 2]
    # personal_post_list.reverse()
    # ret = personal_post_list

    if topic_id == -1:
        personal_post_sort_obj = Post.query.filter(Post.visibility == 1, Post.post_type != 2, Post.uid == uid).order_by(
            Post.post_time.desc())
    else:
        personal_post_sort_obj = Post.query.filter(Post.visibility == 1, Post.post_type != 2, Post.uid == uid,
                                                   Post.topic_id == topic_id).order_by(Post.post_time.desc())

    personal_post_sort_list = personal_post_sort_obj.paginate(page_index, page_size, False)

    marshal_structure = SINGLE_POST_STRUCTURE.copy()
    ret = marshal(personal_post_sort_list.items, marshal_structure)

    pagination = {'limit': len(ret), 'total': len(personal_post_sort_obj.all())}

    return True, {'data': ret, 'pagination': pagination}
