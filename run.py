# coding=utf-8
__author__ = 'smallfly'

from app import app, db

db.create_all()
# print(app.url_map)
if __name__ == "__main__":
    app.config['JSON_AS_ASCII'] = False
    app.run(host="0.0.0.0", port=8001, debug=True)
