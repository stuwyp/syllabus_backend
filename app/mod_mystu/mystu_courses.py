# mode
# 0：课程列表json
# 1：课程详细json
import re
import traceback
from urllib.parse import quote

import requests

pattern_link_id = re.compile('view.php\?id=(\d{1,})')


def get_courses(cookies, start_year, end_year, semester):
    try:
        if end_year - start_year != 1:
            return {'error': 'The parameter of years is wrong '}, 400
        elif semester > 3 or semester < 1:
            return {'error': 'The parameter of semester is wrong '}, 400
        # elif mode != 0 and mode != 1:
        #     print(mode,type(mode))
        #     return {'error': 'The mode of semester is wrong '}

        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Cookie': cookies,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        }

        resp = requests.get('https://my.stu.edu.cn/v3/services/api/course/query?_=1526386545736', headers=header,
                            timeout=3)
        if resp.status_code == 401:
            return {'error': 'cookie expired or wrong cookie'}, 401
        json = resp.json()
        if 'msg' not in json.keys():
            courses_list = json.get('items')
            counter = 0
            all_courses = []
            # print(start_year)
            # if mode == 1:
            for course in courses_list:
                if start_year == course[3] and semester == course[4]:
                    linkid = re.findall(pattern_link_id, course[8])
                    if len(linkid) == 0:
                        continue
                    linkid = linkid[0]
                    if linkid != '0' and ('ELC' not in course[5]):
                        counter += 1
                        all_courses.append(
                            {
                                'courseLinkId': linkid,
                                'courseLink': course[8],
                                'courseName': course[1],
                            })
            print(all_courses)
            return {'courseNum': counter, 'courses': all_courses}, 200
        else:
            return {'error': 'your cookies of account is wrong'}, 401
    except Exception as e:
        print(traceback.print_exc())
        return {'error': 'request error'}, 400
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


def get_index(cookies, pageSize=5, pageNo=1):
    try:
        file_url_prefix = 'https://my.stu.edu.cn/v3/services/openapi/v1/file/show/'
        img_url_add_string = '120_90'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Cookie': cookies,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        }
        url = 'https://my.stu.edu.cn/v3/services/api/post/byCourse?pageSize={}&&pageNo={}&&type=all'.format(pageSize,
                                                                                                            pageNo)

        resp = requests.get(url, headers=header, timeout=3)
        if resp.status_code == 401:
            return {'error': 'cookie expired or wrong cookie'}, 401
        resp_json = resp.json()
        message_list = []
        print(len(resp_json['items']))
        for item in resp_json['items']:
            name = item[3]['fullName']
            content = item[6]
            course_name = item[11]
            files_list = []
            length = 0
            if item[12] is not None:
                length = len(item[12])
                for i in item[12]:

                    file = {
                        'file_url': file_url_prefix + i[0] + '/' + quote(i[1], 'gbk'),
                        'file_name': i[1]
                    }

                    files_list.append(file)
            # print(files_list)
            item_dict = {
                'teacher_name': name,
                'content': content,
                'course_name': course_name,
                'course_files': {'length':length,'course_files_details':files_list}
            }
            # print(item_dict)
            message_list.append(item_dict)
        return message_list, 200
    except Exception as e:
        print(traceback.print_exc())
        return {'error': 'request error'}, 400
