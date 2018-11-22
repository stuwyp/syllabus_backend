# coding=utf-8
__author__ = 'smallfly'

from flask_restful import Resource, reqparse

import requests
import requests.exceptions

post_parser = reqparse.RequestParser(trim=True)

post_parser.add_argument("username", required=True, location="form")
post_parser.add_argument("token", required=True, location="form")
post_parser.add_argument("page_index", location="form")
post_parser.add_argument("page_size", location="form")
post_parser.add_argument("keyword", location="form")
post_parser.add_argument("subcompany_id", location="form")

class OAResource(Resource):

    def post(self):
        args = post_parser.parse_args()
        try:
            resp = requests.post("http://127.0.0.1:8080/stu_oa", data=args)
            return resp.json()
        except requests.exceptions.ConnectionError:
            return {"error": "connection refused"}, 400