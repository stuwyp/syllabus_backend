# coding=utf-8
__author__ = 'smallfly'

# 存放了用户数据, 以及活动之类的互动.

from flask import Blueprint
# 默认在这个blueprint建立的目录中寻找templates
interaction_blueprint = Blueprint(
    "interaction",
    __name__,
    url_prefix="/interaction",
    template_folder='templates'
)  # url 必须以 / 开头

# 加载数据表

# 加载Resource
from app.mod_interaction.resources import UserResource
from app.mod_interaction.resources import PostResource
from app.mod_interaction.resources import CommentResource
from app.mod_interaction.resources import ThumbUpResource

from app.mod_interaction.resources.CommentResource import PersonalCommentResource
from app.mod_interaction.resources.PostCommentResource import PostSortResource, PersonalPostSortResource
from app.mod_interaction.resources.CommentThumbUpResource import CommentThumbUpResource

from app.mod_interaction.resources.GenericSingleResource import GenericSingleResource
from app.mod_interaction.resources.GenericMultipleResource import GenericMultipleResource
from app.mod_interaction.resources.GenericOneToManyRelationResource import GenericOneToManyRelationResource
from app.mod_interaction.resources.VersionResource import VersionResource
from app.mod_interaction.resources.BannerResource import BannerResource
from app.mod_interaction.resources.UserResource import CompatibleUserResource
from app.mod_interaction.resources.LatestResource import LatestResource
from app.mod_interaction.resources.UnreadResource import UnreadResource
from app.mod_interaction.resources.CarpoolResource import CarpoolSResource, CarpoolResource
from app.mod_interaction.resources.PassengerResource import PassengerResource
from app.mod_interaction.resources.ActivityResource import ActivityResource
from app.mod_interaction.resources.CollectorResource import CollectorResource
from app.mod_interaction.resources.SyllabusCollectionResource import SyllabusCollectionResource
from app.mod_interaction.resources.AnonymousPostResource import AnonymousResource, PersonalAnonymousResource

# views
from app.mod_interaction.views import BannerView, UploadBannerView

from flask_restful import Api

api_v2 = Api(interaction_blueprint, prefix="/api/v2")

# ================= 获取单个资源 =================
# curl 127.0.0.1:8080/interaction/api/v2/user/1
# curl --header "Content-type: application/json" 127.0.0.1:8080/interaction/api/v2/user -X PUT -d '{"id": 1, "birthday": "819648000", "nickname": "拂晓", "gender": 1, "profile": "hello world", "token": "000000", "uid": 1}'
# curl -i -X DELETE 127.0.0.1:8080/interaction/api/v2/user/1
api_v2.add_resource(GenericSingleResource, "/user/<int:id>", "/user", endpoint="user",
                    resource_class_kwargs=UserResource.SINGLE_USER_INITIAL_KWARGS)
# 兼容之前课表的接口
api_v2.add_resource(CompatibleUserResource, "/compatible_user/<account>", endpoint="compatible_user")

# curl 127.0.0.1:8080/interaction/api/v2/post/1
# curl 127.0.0.1:8080/interaction/api/v2/post -i --header "Content-type: application/json" -X POST -d '{"title": "testing_title", "content": "haha", "description": "click me", "uid": 1, "post_type": 1, "token": "000000"}'
# curl 127.0.0.1:8080/interaction/api/v2/post -i --header "Content-type: application/json" -X PUT -d '{"title": "testing_title", "content": "haha", "id": 2, "description": "do not click me", "uid": 1, "post_type": 1, "token": "000000"}'
# curl 127.0.0.1:8080/interaction/api/v2/post -i -H "token: 000000" -H "uid: 1" -H "id: 1" -X DELETE
# api.add_resource(PostResource, "/post/<int:id>", "/post", endpoint="post")
api_v2.add_resource(GenericSingleResource, "/post/<int:id>", "/post", endpoint="post",
                    resource_class_kwargs=PostResource.SINGLE_INITIAL_KWARGS)

# curl 127.0.0.1:8080/interaction/api/v2/comment/1
# curl 127.0.0.1:8080/interaction/api/v2/comment -i -X POST -H "Content-type:application/json" -d '{"token": "000000", "post_id": 1, "uid": 1, "comment": "nice post!"}'
# curl 127.0.0.1:8080/interaction/api/v2/comment -i -X PUT -H "Content-type:application/json" -d '{"token": "000000", "id": 1, "post_id": 1, "uid": 1, "comment": "amazing post!"}'
# curl -i -X DELETE 127.0.0.1:8080/interaction/api/v2/comment --header "Content-type:application/json" -d '{ "uid": 1, "token": "00000", "id":1}'
api_v2.add_resource(GenericSingleResource, "/comment/<int:id>", "/comment", endpoint="comment",
                    resource_class_kwargs=CommentResource.SINGLE_USER_INITIAL_KWARGS)

# curl 127.0.0.1:8080/interaction/api/v2/like/1
# curl 127.0.0.1:8080/interaction/api/v2/like -i -X POST -H "Content-type:application/json" -d '{"post_id": 1, "uid": 1, "token": "000000"}'
# curl -i -X DELETE 127.0.0.1:8080/interaction/api/v2/like -H "id: 1" -H "uid: 1" -H "token: 000000"
api_v2.add_resource(GenericSingleResource, "/like/<int:id>", "/like", endpoint="like",
                    resource_class_kwargs=ThumbUpResource.SINGLE_THUMB_UP_INITIAL_KWARGS)
# ================= 获取单个资源 =================

# ================= 获取多个资源 =================
# curl "127.0.0.1:8080/interaction/api/v2/users?field=gender&value=1&offset=2&count=1&sort_type=2&order_by=id"
api_v2.add_resource(GenericMultipleResource, "/users", "/users/", endpoint="users",
                    resource_class_kwargs=UserResource.MULTIPLE_USERS_INITIAL_KWARGS)
api_v2.add_resource(GenericMultipleResource, "/posts", "/posts/", endpoint="posts",
                    resource_class_kwargs=PostResource.MULTIPLE_USERS_INITIAL_KWARGS)
# ================= 获取多个资源 =================

# ================= 寻找一对多的资源 =================
# curl "http://127.0.0.1:8080/interaction/api/v2/post_comments?field=post_id&value=3"
api_v2.add_resource(GenericOneToManyRelationResource, "/post_comments", "/post_comments/", endpoint="post_comments",
                    resource_class_kwargs=CommentResource.QUERY_COMMENTS_FOR_POST_INITIAL_KWARGS)
# ================= 寻找一对多的资源 =================

api_v2.add_resource(VersionResource, "/version", "/version/", endpoint="version")
api_v2.add_resource(BannerResource, "/banner", "/banner/", endpoint="banner")

# ================= 获取最新资源的id =================
api_v2.add_resource(LatestResource, "/latest", "/latest/", endpoint="latest")

# ================= 获取未读消息 =================
api_v2.add_resource(UnreadResource, "/unread", "/unread/", endpoint="unread")

# ================= 拼车消息 =================
# curl "127.0.0.1:8080/interaction/api/v2/carpools?sort_by=name&sort_by=age&order=desc&order=asc"
api_v2.add_resource(CarpoolSResource, "/carpools", "/carpools/", endpoint="carpools")

api_v2.add_resource(CarpoolResource, "/carpool", "/carpool/", endpoint="carpool")

api_v2.add_resource(PassengerResource, "/passenger", "/passenger/", endpoint="passenger")
# ================= 拼车消息 =================

# ================= 活动消息 =================
api_v2.add_resource(ActivityResource, "/activity", "/activity/", endpoint="activity")
# ================= 活动消息 =================

# ================= 申请课表收集 =================
api_v2.add_resource(CollectorResource, "/collector", "/collector/", endpoint="collector")
api_v2.add_resource(SyllabusCollectionResource, "/syllabus_collection", "/syllabus_collection/",endpoint="syllabus_collection")
# ================= 申请课表收集 =================

# ================= 匿名消息 =================
api_v2.add_resource(AnonymousResource, "/anonymous", "/anonymous/", endpoint="anonymous")
# ================= 匿名消息 =================
api_v2.add_resource(CommentThumbUpResource, "/like_on_comment", "/like_on_comment/", endpoint="like_on_comment")
api_v2.add_resource(PostSortResource, "/post_sort", "/post_sort/", endpoint="post_sort")
api_v2.add_resource(PersonalPostSortResource, "/personal_post", "/personal_post/", endpoint="personal_post")
api_v2.add_resource(PersonalAnonymousResource, "/personal_anonymous", "/personal_anonymous/", endpoint="personal_anonymous")
api_v2.add_resource(PersonalCommentResource, "/personal_comment", "/personal_comment/", endpoint="personal_comment")

# ============== 添加views ==============

interaction_blueprint.add_url_rule("/banners", view_func=BannerView.as_view("banners"))
interaction_blueprint.add_url_rule("/upload", view_func=UploadBannerView.as_view("upload"))
