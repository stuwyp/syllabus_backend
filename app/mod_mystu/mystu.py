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
# pattern = re.compile('<input type=.hidden. name=.lt.*?value=.(.*?).>')
# pattern2 = re.compile('<input type=.hidden. name=.execution.*?value=.(.*?).>')
# pattern3 = re.compile('id=.expandable_branch_.*?><a title=.(.*?)href=.(.*?).>.*?')
link_id = re.compile('view.php\?id=(\d{1,})')
pattern_file_rescource = re.compile(
    '.*?href=.(https://my.stu.edu.cn/courses/campus/mod/resource/view.php.*?).>.img.*?/f/(.*?).24.*?instancename.>(.*?)<.*?')
pattern_file_linkid = re.compile('.*?(\d{1,}).*?')
pattern_folder = re.compile(
    '.*?href=.(https://my.stu.edu.cn/courses/campus/mod/folder/view.php)\?id=(\d{1,}).*?instancename.>(.*?)<')

pattern_folder_file = re.compile(
    '.*?href=.(https://my.stu.edu.cn/courses/campus/.*?/mod_folder/content/.*?forcedownload=1).*?/f/(.*?).24.*?fp-filename.>(.*?)<.*?')

loginUrl = "https://sso.stu.edu.cn/login"
coursesUrl = "https://my.stu.edu.cn/courses/campus/my"
folderUrl = 'https://my.stu.edu.cn/courses/campus/mod/folder/view.php'
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
            return {'message': 'password or username is wrong!'}, 401

    strCookie = ""
    for key, value in mystu.cookies.items():
        if key == 'JSESSIONID':
            value = value[:-10]
        str = key + '=' + value + ';'
        strCookie = strCookie + str

    print('登录成功')
    # print(mystu.cookies)
    return {'Cookie': strCookie, 'setCookie': setCookie}, 200, mystu.cookies


# mode
# 0：课程列表json
# 1：课程详细json
def get_courses(cookies, start_year, end_year, semester):
    try:
        if end_year - start_year != 1:
            return {'message': 'The parameter of years is wrong '}, 400
        elif semester > 3 or semester < 1:
            return {'message': 'The parameter of semester is wrong '}, 400
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
        if 'msg' not in json.keys():
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
                                'courseLinkId': linkid,
                                'courseLink': course[8],
                                'courseName': course[1],
                            })

            return {'courseNum': counter, 'courses': allCourses}, 200
        else:
            return {'message': 'your cookies of account is wrong'}, 401
    except Exception as e:
        print(repr(e))
        return {'error': 'Internal Server Error'}, 500
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


def get_files(course_linkid, cookies):
    try:
        t0 = time.time()
        courseFiles = []
        course_url = 'https://my.stu.edu.cn/courses/campus/course/view.php'
        fileUrl = "https://my.stu.edu.cn/courses/campus/mod/resource/view.php?id="

        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Cookie': cookies
        }

        resp = requests.get(course_url, headers=header, params={'id': course_linkid}, timeout=2)

        if "MYSTU/校内办公系统/学分制/网上报修/预约系统" in resp.text:
            response = requests.get(coursesUrl, headers=header, timeout=2)
            if "MYSTU/校内办公系统/学分制/网上报修/预约系统" in response.text:
                return {'message': 'your cookies of account is wrong'}, 401
            else:
                return {'message': 'your linkId of course is wrong'}, 400

        if not '找不到数据记录' in resp.text and not '此课程现在不可自助选课' in resp.text:

            position1 = resp.text.find('"region-main"')
            position2 = resp.text.find('"region-pre"')
            content2_file = resp.text[position1:position2]

            items = re.findall(pattern_file_rescource, content2_file)

            for item in items:
                fileId = re.findall(pattern_file_linkid, item[0])[0]
                courseFiles.append(
                    {
                        # 'fileId': fileId,
                        'fileLink': fileUrl + fileId,
                        'fileKind': item[1],
                        'fileName': item[2]
                    }
                )

            # folder_link_list = re.findall(pattern_folder, content2_file)
            soup = BeautifulSoup(content2_file, 'lxml')
            folder_link_list = soup.find_all('li', attrs={'class': 'activity folder modtype_folder '})
            folder = []

            for item in folder_link_list:
                new_item = re.findall(pattern_folder, str(item))[0]
                folder.append(
                    {
                        'folderLinkId': new_item[1],
                        'folderLink': folderUrl + '?id=' + new_item[1],
                        'folderName': new_item[2]
                    }
                )

            return {'files': courseFiles, 'folders': folder}, 200
        else:
            return {'message': 'your linkId of course is wrong'}, 400
    except Exception as e:
        print(repr(e))
        return {'error': 'Internal Server Error'}, 500


def get_assigns_link(course_linkid, cookies):
    try:
        course_url = 'https://my.stu.edu.cn/courses/campus/course/view.php'
        t0 = time.time()
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Cookie': cookies
        }

        html = requests.get(course_url, headers=header, params={'id': course_linkid}, timeout=2).text
        if "MYSTU/校内办公系统/学分制/网上报修/预约系统" in html:
            response = requests.get(coursesUrl, headers=header, timeout=2)
            if "MYSTU/校内办公系统/学分制/网上报修/预约系统" in response.text:
                return {'message': 'your cookies of account is wrong'}, 401
            else:
                return {'message': 'your linkId of course is wrong'}, 400
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
                try:
                    content = str(content)
                    soup2 = BeautifulSoup(content, 'lxml')
                    find_link = soup2.find('a')
                    find_title = soup2.find('span', attrs={'class': 'instancename'}).get_text()
                    # print(find_link)
                    link = find_link.get('href')
                    course_linkid = re.findall(link_id, link)[0]
                    count += 1
                    assignslink.append({'assignLink': link, 'assignLinkId': course_linkid, 'assignTitle': find_title})
                except Exception as e:
                    print(repr(e))
                    continue
            # print(assign)
            t1 = time.time()
            print(t1 - t0)
            return {'num': count, 'assigns': assignslink}, 200
        else:
            return {'message': 'your linkId of course is wrong'}, 400
    except Exception as e:
        print(repr(e))
        return {'error': 'Internal Server Error'}, 500


def get_assignment(assign_linkid, cookies):
    try:
        # assigns = get_assign_link(linkid, cookies)
        # print(linkid)
        assign_url = 'https://my.stu.edu.cn/courses/campus/mod/assign/view.php'
        assignment_url = 'https://my.stu.edu.cn/courses/campus/mod/assignment/view.php'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Cookie': cookies
        }
        # print(assign_url)
        html = requests.get(assign_url, headers=header, params={'id': assign_linkid}, timeout=1.5).text
        if "MYSTU/校内办公系统/学分制/网上报修/预约系统" in html:
            return {'message': 'your cookies of account is wrong'}, 401
        elif '错误的更多信息' not in html:
            status = {}
            soup = BeautifulSoup(html, 'lxml')
            find_assign = soup.find('div', attrs={'class': 'no-overflow'})
            if find_assign:
                assignText = find_assign.get_text()
            else:
                assignText = None

            status.update({'assign': assignText})
            contents = soup.find_all('div', attrs={'id': 'dates'})
        else:
            html_ = requests.get(assignment_url, headers=header, params={'id': assign_linkid}, timeout=1.5).text
            if "MYSTU/校内办公系统/学分制/网上报修/预约系统" in html_:
                return {'message': 'your cookies of account is wrong'}, 401
            elif '错误的更多信息' not in html_:
                status = {}
                soup = BeautifulSoup(html_, 'lxml')
                find_assign = soup.find('div', attrs={'class': 'no-overflow'})
                if find_assign:
                    assignText = find_assign.get_text()
                else:
                    assignText = None

                status.update({'assign': assignText})
                contents = soup.find_all('div', attrs={'id': 'dates'})
            else:
                return {'message': "assign_linkid forbidden"}, 403

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
            contents = soup.find_all('div', attrs={'class': 'submissionstatustable'})
            # print(str(contents))
            if contents:
                soup2 = BeautifulSoup(str(contents), 'lxml')
                find_tr = soup2.find_all('tr')
                status.update({'beginTime': None})
                status.update({'endTime': None})
                status.update({'submitStatus': None})
                status.update({'gradeStatus': None})
                for tr in find_tr:

                    tr = tr.text.strip('\n')
                    # print(tr)
                    if '截止时间' in tr:
                        status.update({'endTime': tr[5:]})
                        continue

                    if '提交状态' in tr:
                        status.update({'submitStatus': tr[5:]})
                        continue

                    if '评分状态' in tr:
                        status.update({'gradeStatus': tr[5:]})
                        continue
                find_feedback = soup.find_all('div', attrs={'class': 'feedback'})
                # print(find_feedback)
                if find_feedback:
                    soup2 = BeautifulSoup(str(find_feedback), 'lxml')
                    find_tr = soup2.find_all('tr')
                    for tr in find_tr:
                        tr = tr.text.strip('\n')
                        if '成绩' in tr:
                            grade = tr[3:].split('/')[0].strip()
                            status.update({'grade': grade})
                            status.pop('gradeStatus')
                            break
                        else:
                            status.update({'grade': None})
        return status, 200
    except Exception as e:
        print(repr(e))
        return {'error': 'Internal Server Error'}, 500


def get_folder_files(folder_id, cookies):
    try:
        t0 = time.time()
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Cookie': cookies
        }

        resp = requests.get(folderUrl, headers=header, params={'id': folder_id}, timeout=1.5)
        if "MYSTU/校内办公系统/学分制/网上报修/预约系统" in resp.text:
            return {'message': 'your cookies of account is wrong'}, 401
        # print(resp.text)
        # t1 = time.time()
        # print(t1 - t0)
        if not '找不到数据记录' in resp.text and not '此课程现在不可自助选课' in resp.text:
            courseFiles = []
            counter = 0
            soup = BeautifulSoup(resp.text, 'lxml')
            a_list = soup.find_all('span', class_='fp-filename-icon')

            for item in a_list:
                counter += 1
                new_item = re.findall(pattern_folder_file, str(item))[0]
                courseFiles.append(
                    {
                        'fileLink': new_item[0],
                        'fileKind': new_item[1],
                        'fileName': new_item[2]
                    }
                )
            t1 = time.time()
            print(t1 - t0)
            return {'fileNum': counter, 'files': courseFiles}, 200
        else:
            return {'message': 'your linkId of folder is wrong'}, 400
    except Exception as e:
        print(repr(e))
        return {'error': 'Internal Server Error'}, 500


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
    # res = get_files(12790,'CASTGC=TGT-107846-leBnI3kPAnWMa2ZazEAvObJtjb7MfCpapjdmmHJtZFmkdPresb-cas51;MoodleSession=te5m7djsbtbin0kd28ctvqa4q2;_UT_=9107AF284ADC11E6B11A0050568C74A4|29e1ff29-4c0c-4ca4-9830-7fa01f130aca;JSESSIONID=773EBDBAF4A;username=16ypwang;')
