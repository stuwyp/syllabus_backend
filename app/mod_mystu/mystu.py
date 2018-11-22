import time
from flask import Flask
from http.cookiejar import CookieJar
import requests
import re
from lxml import etree
from bs4 import BeautifulSoup

cookie = {}
t0 = 0
app = Flask(__name__)
pattern = re.compile('<input type=.hidden. name=.lt.*?value=.(.*?).>')
pattern2 = re.compile('<input type=.hidden. name=.execution.*?value=.(.*?).>')
pattern3 = re.compile('id=.expandable_branch_.*?><a title=.(.*?)href=.(.*?).>.*?')
pattern4 = re.compile(
    '.*?href=(.https://my.stu.edu.cn/courses/campus/mod/resource/view.php.*?).>.img.*?/f/(.*?).24.*?instancename.>(.*?)<.*?')
pattern5 = re.compile('.*?(\d{1,}).*?')
link_id = re.compile('view.php\?id=(\d{1,})')

loginUrl = "https://sso.stu.edu.cn/login"
coursesUrl = "https://my.stu.edu.cn/courses/campus/my"
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

        print('exist')
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
            return {'message': 'password or username is wrong!'}, {}

    strCookie = ""
    for key, value in mystu.cookies.items():
        if key == 'JSESSIONID':
            value = value[:-10]
        str = key + '=' + value + ';'
        strCookie = strCookie + str

    print('登录成功')
    return {'cookies': strCookie, 'setCookie': setCookie}, mystu.cookies


# mode
# 0：课程列表json
# 1：课程详细json
def show_courses(cookies, start_year, end_year, semester):
    if end_year - start_year != 1:
        return {'message': 'The parameter of years is wrong '}
    elif semester > 3 or semester < 1:
        return {'message': 'The parameter of semester is wrong '}
    # elif mode != 0 and mode != 1:
    #     print(mode,type(mode))
    #     return {'message': 'The mode of semester is wrong '}
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Cookie': cookies,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }

    json = requests.get('https://my.stu.edu.cn/v3/services/api/course/query?_=1526386545736', headers=header,
                        timeout=1.5).json()
    coursesList = json.get('items')
    counter = 0
    allCourses = []
    # print(start_year)
    # if mode == 1:
    for course in coursesList:
        # print(course[3])
        if start_year == course[3] and semester == course[4]:
            linkid = re.findall(link_id, course[8])[0]
            if linkid != '0' and ('ELC' not in course[5]):
                counter += 1
                allCourses.append(
                    {
                        'linkId': linkid,
                        'courseLink': course[8],
                        'courseName': course[1],
                    })

    return {'courseNum': counter, 'courses': allCourses}

    # else:
    #     for course in coursesList:
    #         if start_year == course[3] and semester == course[4]:
    #             linkid = re.findall(link_id, course[8])[0]
    #             counter += 1
    #             allCourses.append(
    #                 {
    #                     'courseName': course[1],
    #                     'courseCode':course[5],
    #                     'classCode':course[7]
    #                 })
    #
    #
    #     return {'courseNum': counter, 'courses': allCourses}


def show_files(linkid, cookies):
    courseFiles = []
    course_url = 'https://my.stu.edu.cn/courses/campus/course/view.php'
    fileUrl = "https://my.stu.edu.cn/courses/campus/mod/resource/view.php?id="

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Cookie': cookies
    }

    resp = requests.get(course_url, headers=header, params={'id': linkid}, timeout=1.5)
    if "MYSTU/校内办公系统/学分制/网上报修/预约系统" in resp.text:
        return {'message': 'your cookies of account is wrong'}
    if not '找不到数据记录' in resp.text and not '此课程现在不可自助选课' in resp.text:

        position1 = resp.text.find('"region-main"')
        position2 = resp.text.find('"region-pre"')
        content2_file = resp.text[position1:position2]

        items4 = re.findall(pattern4, content2_file)
        counter = 0
        for item in items4:
            fileId = re.findall(pattern5, item[0])[0]
            counter += 1
            courseFiles.append(
                {
                    'fileId': fileId,
                    'fileLink': fileUrl + fileId,
                    'fileKind': item[1],
                    'fileName': item[2]
                }
            )

        return {'fileNum': counter, 'files': courseFiles}
    else:
        return {'message': 'your linkId of course is wrong'}


def get_assign_link(linkid, cookies):
    course_url = 'https://my.stu.edu.cn/courses/campus/course/view.php'
    t0 = time.time()
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Cookie': cookies
    }

    html = requests.get(course_url, headers=header, params={'id': linkid}, timeout=1.5).text
    if "MYSTU/校内办公系统/学分制/网上报修/预约系统" in html:
        return {'message': 'your cookies of account is wrong'}
    t1 = time.time()
    print(t1 - t0)
    assignslink = []
    if not '找不到数据记录' in html and not '此课程现在不可自助选课' in html:
        soup = BeautifulSoup(html, 'lxml')

        # contents1 = soup.find_all('li', attrs={'class': 'activity assignment modtype_assignment '})
        # contents2 = soup.find_all('li', attrs={'class': 'activity assign modtype_assign '})
        # contents = contents1 + contents2
        contents = soup.find_all('li', attrs={
            'class': re.compile('activity assignment modtype_assignment |activity assign modtype_assign ')})
        count = 0
        for content in contents:
            content = str(content)
            soup2 = BeautifulSoup(content, 'lxml')
            find_link = soup2.find('a')
            find_title = soup2.find('span', attrs={'class': 'instancename'}).get_text()
            link = find_link.get('href')
            linkid = re.findall(link_id, link)[0]
            count += 1
            assignslink.append({'link': link, 'linkid': linkid, 'title': find_title})
        # print(assign)
        t1 = time.time()
        print(t1 - t0)
        return {'num': count, 'assign': assignslink}
    else:
        return None


def show_assigns(linkid, cookies):
    # assigns = get_assign_link(linkid, cookies)
    # print(linkid)
    assign_url = 'https://my.stu.edu.cn/courses/campus/mod/assign/view.php'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Cookie': cookies
    }
    # print(assign_url)
    html = requests.get(assign_url, headers=header, params={'id': linkid}, timeout=1.5).text
    if "MYSTU/校内办公系统/学分制/网上报修/预约系统" in html:
        return {'message': 'your cookies of account is wrong'}
    status = {}
    soup = BeautifulSoup(html, 'lxml')
    find_assign = soup.find('div', attrs={'class': 'no-overflow'})
    if find_assign:
        assignText = find_assign.get_text()
    else:
        assignText = None

    status.update({'assgin': assignText})
    contents = soup.find_all('div', attrs={'id': 'dates'})

    if contents:
        soup2 = BeautifulSoup(str(contents), 'lxml')
        find_tr = soup2.find_all('tr')
        for tr in find_tr:
            tr = tr.text
            if tr.startswith('开放时间'):
                status.update({'beginTime': tr[6:]})
            elif tr.startswith('截止时间'):
                status.update({'endTime': tr[6:]})
            else:
                status.update({'time': tr})

    else:
        contents = soup.find_all('table', attrs={'class': 'generaltable'})
        if contents:
            soup2 = BeautifulSoup(str(contents), 'lxml')
            find_tr = soup2.find_all('tr')
            for tr in find_tr:
                tr = tr.text.strip('\n')
                status.update({'beginTime': None})
                if '截止时间' in tr:
                    status.update({'endTime': tr[5:]})

    return status


def transferTerm(term):
    if '秋' in term:
        semester = 1
    elif '春' in term:
        semester = 2
    else:
        semester = 3

    item = int(re.findall(pattern5, term)[0])
    if semester == 2:
        year = item - 1
    else:
        year = item
    year = str(year) + '-' + str(year + 1)
    return year, semester