# coding=utf-8

from flask import Blueprint
# 不使用蓝图时 需要这行代码
# from app import app

from flask_restful import Api

from app.mod_smartcard.resources.card_resource import CardBalanceResource, CardDetailResource

smartcard_blueprint = Blueprint(
    "card",
    __name__,
    url_prefix="/card",
)  # url 必须以 / 开头

api_v2 = Api(smartcard_blueprint, prefix="/api/v2")

# 不用蓝图时，Api 必须使用app初始化
# api_v2 = Api(app, prefix="/api/v2")

api_v2.add_resource(CardBalanceResource, "/balance", "/balance/", endpoint="balance")
api_v2.add_resource(CardDetailResource, "/detail", "/detail/", endpoint="detail")