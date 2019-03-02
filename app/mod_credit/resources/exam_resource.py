# coding=utf-8
__author__ = 'smallfly'

from flask_restful import Resource, reqparse

import requests
import requests.exceptions

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
}

parser = reqparse.RequestParser(trim=True)

parser.add_argument("username", required=True, location="form")
parser.add_argument("password", required=True, location="form")
parser.add_argument("years", required=True, location="form")
parser.add_argument("semester", required=True, location="form")
parser.add_argument('Cookie', location='headers')


class ExamResource(Resource):

    def post(self):
        args = parser.parse_args()
        if args['Cookie'] is not None:
            HEADERS['Cookie'] = args['Cookie']
            args.pop('Cookie')
        try:
            resp = requests.post("http://127.0.0.1:8080/exam", headers=HEADERS, data=args)
            # print(resp.headers)
            return resp.json(), 200, {'Cookie': resp.headers['Cookie']}
        except requests.exceptions.ConnectionError:
            return {"error": "connection refused"}, 400
