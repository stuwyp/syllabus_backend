import time
import traceback

from flask import Flask
from http.cookiejar import CookieJar
import requests
import re
from lxml import etree
from bs4 import BeautifulSoup

cookie = {}
t0 = 0
app = Flask(__name__)

# folderUrl = 'https://my.stu.edu.cn/courses/campus/mod/folder/view.php'
# pattern = re.compile('<input type=.hidden. name=.lt.*?value=.(.*?).>')
# pattern2 = re.compile('<input type=.hidden. name=.execution.*?value=.(.*?).>')
# pattern3 = re.compile('id=.expandable_branch_.*?><a title=.(.*?)href=.(.*?).>.*?')
# link_id = re.compile('view.php\?id=(\d{1,})')
# pattern_file_rescource = re.compile(
#     '.*?href=.(https://my.stu.edu.cn/courses/campus/mod/resource/view.php.*?).>.img.*?/f/(.*?).24.*?instancename.>(.*?)<.*?')

# pattern_folder = re.compile(
#     '.*?href=.(https://my.stu.edu.cn/courses/campus/mod/folder/view.php)\?id=(\d{1,}).*?instancename.>(.*?)<')
#
# pattern_folder_file = re.compile(
#     '.*?href=.(https://my.stu.edu.cn/courses/campus/.*?/mod_folder/content/.*?forcedownload=1).*?/f/(.*?).24.*?fp-filename.>(.*?)<.*?')
#
loginUrl = "https://sso.stu.edu.cn/login"
coursesUrl = "https://my.stu.edu.cn/courses/campus/my"
pattern_file_linkid = re.compile('.*?(\d{1,}).*?')
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
}


class Mystu(object):
    # 初始化构造函数，账号和密码
    def __init__(self, username, password, cookies={}):
        self.session = None
        self.loginStatus = False
        self.cookies = {}
        self.newCookie = False
        self.moodleSession = None

    def setSession(self, session):
        self.session = session

    def getSession(self):
        return self.session

    # 返回一个登陆成功后的Response
    def toLoginWithCookies(self, cookies):
        # print(cookies)
        # print('exist')
        session = requests.Session()

        session.cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)

        session.post(loginUrl, headers=headers)

        self.setLoginStatus(session)

        if self.getLoginStatus():
            session.cookies.update(cookies)
            self.cookies = cookies
            self.setSession(session)

            return True
        else:
            return False

    def toLogin(self, username, password):
        session = requests.Session()

        session.cookies = CookieJar()

        # 得到一个Response对象，但是此时还没有登录
        resp = session.get(coursesUrl, headers=headers)

        # self.moodleSession = requests.utils.dict_from_cookiejar(session.cookies).get('MoodleSession')
        # print(requests.utils.dict_from_cookiejar(session.cookies))

        html = etree.HTML(resp.text)

        lt = html.xpath('//*[@id="fm1"]/input[1]/@value')[0]

        postData = {
            '_eventId': 'submit',
            'execution': 'e1s1',
            'lt': lt,
            'username': username,
            'password': password
        }

        # 使用构建好的PostData重新登录,以更新Cookie
        session.post(loginUrl, data=postData, headers=headers)

        self.setLoginStatus(session)

        if self.getLoginStatus():

            self.cookies = requests.utils.dict_from_cookiejar(session.cookies)
            self.setSession(session)
            return True
        else:
            return False

    def setLoginStatus(self, session):
        self.loginStatus = False
        if session is not None:
            resp = session.get(loginUrl, headers=headers)

            # print(resp.text)
            if not "username" in resp.text:
                self.loginStatus = True

    def getLoginStatus(self):
        return self.loginStatus


def get_cookies_after_login(username, password, cookies={}):
    try:
        mystu = Mystu(username, password)

        if cookies and cookies.get('username') == username:
            mystu.toLoginWithCookies(cookies)
            setCookie = False
        else:
            mystu.toLogin(username, password)
            setCookie = True

        if not mystu.loginStatus:
            print('登录中')
            status = mystu.toLogin(username, password)
            if status:
                setCookie = True
            else:
                print('登录失败')
                return {'error': 'password or username is wrong!'}, 401

        strCookie = ""
        for key, value in mystu.cookies.items():
            if key == 'JSESSIONID':
                value = value[:-10]
            str = key + '=' + value + ';'
            strCookie = strCookie + str

        print('登录成功')
        # print(mystu.cookies)
        return {'Cookie': strCookie, 'setCookie': setCookie}, 200, mystu.cookies
    except Exception as e:
        print(traceback.print_exc())
        return {'error': 'request error'}, 400



def transferTerm(term):
    if '秋' in term:
        semester = 1
    elif '春' in term:
        semester = 2
    else:
        semester = 3

    item = int(re.findall(pattern_file_linkid, term)[0])
    if semester == 2:
        year = item - 1
    else:
        year = item
    year = str(year) + '-' + str(year + 1)
    return year, semester


if __name__ == '__main__':
    pass