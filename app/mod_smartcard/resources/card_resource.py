import datetime

import requests
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.mod_smartcard.operations.card_data_operation import get_card_balance, get_card_detail, parse_card_detail
from app.mod_smartcard.operations.card_login_operation import get_cookie
from app.mod_smartcard.operations.helper import dict2string, before_n_days, string2dict

now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day


class CardBalanceResource(Resource):
    def __init__(self):
        super(CardBalanceResource, self).__init__()
        self.post_parser = RequestParser(trim=True)

    def post(self):
        self.post_parser.add_argument("username", required=True, location="form")
        self.post_parser.add_argument("password", required=True, location="form")
        self.post_parser.add_argument('Cookie', location="headers")
        args = self.post_parser.parse_args()
        try:
            if args['Cookie'] is not None:

                print('exist cookie')
                cookie = (string2dict(args['Cookie'])[1])
                # print(cookie)
                ret_balance = get_card_balance(cookie)
                if ret_balance[0]:
                    return {'balance': ret_balance[1]}, 200, {'Cookie': dict2string(cookie)[1]}
                else:
                    print("cookie expired")

            else:
                print("no cookie")

            ret = get_cookie(args['username'], args['password'])
            print(ret)
            if ret[0]:
                cookie = ret[1]
                # print(type(cookie), cookie)
                ret_balance = get_card_balance(cookie)
                if ret_balance[0]:
                    return {'balance': ret_balance[1]}, 200, {'Cookie': dict2string(cookie)[1]}
                else:
                    return {"error": ret_balance[1]}, 400
            else:
                return {"error": "unauthorized"}, 401

        except Exception as e:
            print(repr(e))
            return {"error": repr(e)}, 500


class CardDetailResource(Resource):
    def __init__(self):
        super(CardDetailResource, self).__init__()
        self.post_parser = RequestParser(trim=True)

    def post(self):
        self.post_parser.add_argument("username", required=True, location="form")
        self.post_parser.add_argument("password", required=True, location="form")
        self.post_parser.add_argument("days", type=int, required=True, location="form")
        self.post_parser.add_argument('Cookie', location="headers")
        args = self.post_parser.parse_args()

        try:

            ret_date = before_n_days(args['days'], year, month, day)
            if ret_date[0]:
                start_year, start_month, start_day = ret_date[1:4]
            else:
                start_year, start_month, start_day = year, month, day

            if args['Cookie'] is not None:
                print('exist cookie')
                cookie = (string2dict(args['Cookie'])[1])
                # print(cookie)
                ret_html = get_card_detail(cookie, start_year, start_month, start_day, year, month, day)

                if ret_html[0]:
                    ret_list = parse_card_detail(ret_html[1])
                    if ret_list[0]:
                        length = len(ret_list[1])
                        return {'detail': ret_list[1], 'length': length}, 200,{'Cookie': dict2string(cookie)[1]}
                else:
                    print("cookie expired")

            else:
                print("no cookie")

            ret = get_cookie(args['username'], args['password'])
            if ret[0]:
                cookie = ret[1]
                # print(type(cookie), cookie)
                ret_html = get_card_detail(cookie, start_year, start_month, start_day, year, month, day)

                if ret_html[0]:
                    ret_list = parse_card_detail(ret_html[1])
                    if ret_list[0]:
                        length = len(ret_list[1])
                        return {'detail': ret_list[1], 'length': length}, 200,{'Cookie': dict2string(cookie)[1]}

                return {"error": "error"}, 400

            else:
                return {"error": "unauthorized"}, 401

        except Exception as e:
            print(repr(e))
            return {"error": repr(e)}, 500

        # ret = get_cookie(args['username'], args['password'])
        #
        # if ret[0]:
        #     cookie = ret[1]
        #
        #     try:
        #         ret_date = before_n_days(args['days'], year, month, day)
        #         if ret_date[0]:
        #             start_year, start_month, start_day = ret_date[1:4]
        #         else:
        #             start_year, start_month, start_day = year, month, day
        #         # print(start_year, start_month, start_day, end_year, end_month, end_day)
        #         ret_html = get_card_detail(cookie, start_year, start_month, start_day, year, month, day)
        #
        #         if ret_html[0]:
        #             ret_list = parse_card_detail(ret_html[1])
        #             if ret_list[0]:
        #                 length = len(ret_list[1])
        #                 return {'detail': ret_list[1], 'length': length}, 200
        #
        #         return {"error": "error"}, 400
        #     except Exception as e:
        #         print(repr(e))
        #         return {"error": repr(e)}, 500
        # else:
        #     return {"error": "unauthorized"}, 401


if __name__ == '__main__':
    pass
    # ret = get_card_data('', '', 50)
    # # print(ret[1],ret[2])
    # balance = ret[1][1]
    # ret_json = parse_card_detail(ret[2])
    # # print(ret[2])
    # print(balance)
    # pprint(ret_json)

# ret1 = get_card_balance(cookie[1])
# print(ret1[1])
# ret2 = get_card_detail(cookie[1], 2018, 12, 28, 2019, 1, 28)
# print(ret2[1])
