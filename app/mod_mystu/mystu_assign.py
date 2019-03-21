import re
import time
import traceback

import requests
from bs4 import BeautifulSoup

pattern_link_id = re.compile('view.php\?id=(\d{1,})')
coursesUrl = 'https://my.stu.edu.cn/courses/campus/my'


def get_assigns_link(course_linkid, cookies):
    try:
        course_url = 'https://my.stu.edu.cn/courses/campus/course/view.php'
        t0 = time.time()
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Cookie': cookies
        }
        print(course_url + "?id=" + course_linkid)
        html = requests.get(course_url, headers=header, params={'id': course_linkid}, timeout=3).text
        if 'MYSTU/校内办公系统/学分制/网上报修/预约系统' in html:
            response = requests.get(coursesUrl, headers=header, timeout=3)
            if 'MYSTU/校内办公系统/学分制/网上报修/预约系统' in response.text:
                return {'error': 'cookie expired or wrong cookie'}, 401
            else:
                return {'error': 'linkId of course is wrong'}, 400
        t1 = time.time()
        print(t1 - t0)
        assignslink = []

        if '找不到数据记录' not in html and '此课程现在不可自助选课' not in html:
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
                    course_linkid = re.findall(pattern_link_id, link)[0]
                    count += 1
                    assignslink.append({'assignLink': link, 'assignLinkId': course_linkid, 'assignTitle': find_title})
                except Exception as e:
                    print(traceback.print_exc())
                    continue
            # print(assign)
            t1 = time.time()
            print(t1 - t0)
            return {'num': count, 'assigns': assignslink}, 200
        else:
            return {'error': 'linkId of course is wrong'}, 400
    except Exception as e:
        print(traceback.print_exc())
        return {'error': 'request error'}, 400


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
        if 'MYSTU/校内办公系统/学分制/网上报修/预约系统' in html:
            return {'error': 'cookie expired or wrong cookie'}, 401
        elif '错误的更多信息' not in html:
            status = {}
            soup = BeautifulSoup(html, 'lxml')
            find_assign = soup.find('div', attrs={'class': 'no-overflow'})
            if find_assign:
                assign_text = find_assign.getText('\n', '<br/>')
            else:
                assign_text = None

            status.update({'assign': assign_text})
            contents = soup.find_all('div', attrs={'id': 'dates'})
        else:
            html_ = requests.get(assignment_url, headers=header, params={'id': assign_linkid}, timeout=1.5).text
            if 'MYSTU/校内办公系统/学分制/网上报修/预约系统' in html_:
                return {'error': 'cookie expired or wrong cookie'}, 401
            elif '错误的更多信息' not in html_:
                status = {}
                soup = BeautifulSoup(html_, 'lxml')
                find_assign = soup.find('div', attrs={'class': 'no-overflow'})
                if find_assign:
                    assign_text = find_assign.getText('\n', '<br/>')
                else:
                    assign_text = None

                status.update({'assign': assign_text})
                contents = soup.find_all('div', attrs={'id': 'dates'})
            else:
                return {'error': 'assign_linkid forbidden'}, 403

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
        print(traceback.print_exc())
        return {'error': 'request error'}, 400
