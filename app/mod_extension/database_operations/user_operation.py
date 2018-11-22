# coding = utf-8
from app.models import User

def get_user_by_account(account):
    return User.query.filter_by(account=account).first()


def get_user_by_id(id):
    return User.query.filter_by(id=id).first()
