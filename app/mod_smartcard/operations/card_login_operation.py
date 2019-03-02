# coding=utf-8
import http
import re
import requests

from app.mod_smartcard.operations.helper import str2bytes

WECHAT_STU_LOGIN_URL = 'http://wechat.stu.edu.cn/wechat/login/login_verify'


class SmartCard(object):

    def login(self, username, password, openid):
        post_data = {
            "ldap_account": username,
            "ldap_password": password,
            "btn_ok": "登录",
            "source_type": "dorm_information",
            "openid": openid
        }

        try:
            resp = requests.post(WECHAT_STU_LOGIN_URL, data=post_data)
            if resp.ok:
                if "账号或者密码错误" in resp.text:
                    return False, 'username or password is wrong'
                else:
                    return True
        except requests.RequestException as e:
            print(e)
            return False


def login_with_openid(username, password, openid):
    card = SmartCard()
    return card.login(username, password, openid)


def get_cookie(username, password):
    openid = str2bytes(username)
    url = 'http://wechat.stu.edu.cn/wechat/smartcard/index?openid=' + openid
    resp = requests.get(url)

    if '抱歉，出错了' in resp.text:
        print("--------------------1-----------------------")
        login_with_openid(username, password, openid)
        url = 'http://wechat.stu.edu.cn/wechat/smartcard/index?openid=' + openid
        resp = requests.get(url)
        if '抱歉，出错了' in resp.text:
            print("--------------------2-----------------------")
            print("username or password is wrong")
            return False, "username or password is wrong"

    cookie = requests.utils.dict_from_cookiejar(resp.cookies)
    return True, cookie
