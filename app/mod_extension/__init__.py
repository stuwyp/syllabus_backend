# coding=utf-8

from flask import Blueprint
# 不使用蓝图时 需要这行代码
# from app import app
from app.mod_extension.resources.FindLostResource import FindLostResource, FindLostResources, PersonalFindLostResources
from app.mod_extension.resources.EvaResource import EvaluationResource, ClassEvaluationResource

from app.mod_extension.resources.TodoResource import TodoResource, TodoStatusResource  # 加载Resource
from flask_restful import Api

# 默认在这个blueprint建立的目录中寻找templates
extension_blueprint = Blueprint(
    "extension",
    __name__,
    url_prefix="/extension",
)  # url 必须以 / 开头

api_v2 = Api(extension_blueprint, prefix="/api/v2")

# 不用蓝图时，Api 必须使用app初始化
# api_v2 = Api(app, prefix="/api/v2")

api_v2.add_resource(TodoResource, "/todo", "/todo/", endpoint="todo")
api_v2.add_resource(TodoStatusResource, "/todo_status", "/todo_status/", endpoint="todo_status")

api_v2.add_resource(EvaluationResource, "/eva", "/eva/", endpoint="eva")
api_v2.add_resource(ClassEvaluationResource, "/class_eva", "/class_eva/", endpoint="class_eva")
api_v2.add_resource(FindLostResource, "/findlost/<int:id>", "/findlost", endpoint="findlost")
api_v2.add_resource(FindLostResources, "/findlosts", "/findlosts/", endpoint="findlosts")
api_v2.add_resource(PersonalFindLostResources, "/personal_findlosts", "/personal_findlosts/", endpoint="personal_findlosts")
# api_v2.add_resource(TodoStatusResource, "/todo_status", "/todo_status", endpoint="todo_status")


# api_v2.add_resource(CompatibleUserResource, "/compatible_user/<account>", endpoint="compatible_user")


# api_v2.add_resource(GenericSingleResource, "/post/<int:id>", "/post", endpoint="post", resource_class_kwargs=PostResource.SINGLE_INITIAL_KWARGS)


# ============== 添加views ==============

# extension_blueprint.add_url_rule("/banners", view_func=BannerView.as_view("banners"))
# extension_blueprint.add_url_rule("/upload", view_func=UploadBannerView.as_view("upload"))
