import datetime
import re
from pprint import pprint

import requests

from app.mod_smartcard.operations.card_login_operation import login_with_openid, get_cookie
from app.mod_smartcard.operations.helper import change_datetime_form, str2bytes, before_n_days

CARD_BALANCE_URL = 'http://wechat.stu.edu.cn/wechat/smartcard/Smartcard_cardbalance'
CARD_DETAIL_URL = 'http://wechat.stu.edu.cn/wechat/smartcard/smartcard_trans_detail_result'



def get_card_balance(cookie):
    html = requests.get(CARD_BALANCE_URL, cookies=cookie).text
    pattern = re.compile('.*?一卡通余额是(\d{1,}\.\d{1,2})元')
    balance_ret = re.findall(pattern, html)
    if len(balance_ret) > 0:
        balance = balance_ret[0]
        # print(balance)
        return True, balance
    else:
        return False, None


def get_card_detail(cookie, start_year, start_month, start_day, end_year, end_month, end_day):
    params = {
        'start_year': start_year,
        'start_month': start_month,
        'start_day': start_day,
        'end_year': end_year,
        'end_month': end_month,
        'end_day': end_day
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    }
    resp = requests.get(CARD_DETAIL_URL, params=params, headers=headers, cookies=cookie)
    # print(resp.text)
    # pattern = re.compile('时间:\d{4}年\d{1,2}月\d{1,2}日 \d{1,2}时\d{1,2}分:\d{1,2}秒.*?-3.9元.*?类型:(\w{1,})')
    if '登录' in resp.text:
        return False,None
    else:
        return True, resp.text


def parse_card_detail(html=None):
    # with open("2.html", "r+", encoding='utf-8') as f:
    #     html = f.read()
    # print(html)
    pattern = re.compile(
        '时间:(\d{4}年\d{1,2}月\d{1,2}日 \d{1,2}时\d{1,2}分:\d{1,2}秒).*?(-{0,1}(\d{1,}|\d{1,}\.\d{1,2}))元.*?类型:(\w{1,}).*?名称:(\w{1,}).*?(备注:(\w{1,});?){0,1}</p>')
    item_list = re.findall(pattern, html)
    detail_list = []
    for item in item_list:
        # print(item)
        date_time = change_datetime_form(item[0])
        tem_dict = {
            'date': date_time[1],
            'time': date_time[2],
            'flow': item[1],
            'kind': item[3],
            'name': item[4],
            'note': item[6]
        }
        detail_list.append(tem_dict)
    return True, detail_list


# def get_card_data(username, password, before_days=1, end_year=year, end_month=month, end_day=day):
#     cookie = get_cookie(username, password)
#     ret1 = get_card_balance(cookie)
#
#     ret_date = before_n_days(before_days, end_year, end_month, end_day)
#     if ret_date[0]:
#         start_year, start_month, start_day = ret_date[1:4]
#     else:
#         start_year, start_month, start_day = year, month, day
#         end_year, end_month, end_day = year, month, day
#     # print(start_year, start_month, start_day, end_year, end_month, end_day)
#     ret2 = get_card_detail(cookie, start_year, start_month, start_day, end_year, end_month, end_day)
#     return True, ret1, ret2[1], cookie
# # ret = card_detail_parser()

# pprint(ret)
