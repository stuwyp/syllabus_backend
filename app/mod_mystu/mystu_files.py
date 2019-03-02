import re
import time

import requests
from bs4 import BeautifulSoup

folderUrl = 'https://my.stu.edu.cn/courses/campus/mod/folder/view.php'
coursesUrl = "https://my.stu.edu.cn/courses/campus/my"

pattern_file_rescource = re.compile(
    '.*?href=.(https://my.stu.edu.cn/courses/campus/mod/resource/view.php.*?).>.img.*?/f/(.*?).24.*?instancename.>(.*?)<.*?')
pattern_file_linkid = re.compile('.*?(\d{1,}).*?')
pattern_folder = re.compile(
    '.*?href=.(https://my.stu.edu.cn/courses/campus/mod/folder/view.php)\?id=(\d{1,}).*?instancename.>(.*?)<')
pattern_folder_file = re.compile(
    '.*?href=.(https://my.stu.edu.cn/courses/campus/.*?/mod_folder/content/.*?forcedownload=1).*?/f/(.*?).24.*?fp-filename.>(.*?)<.*?')


def get_files(course_linkid, cookies):
    try:
        t0 = time.time()
        courseFiles = []
        course_url = 'https://my.stu.edu.cn/courses/campus/course/view.php?id='
        fileUrl = "https://my.stu.edu.cn/courses/campus/mod/resources/view.php?id="

        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Cookie': cookies
        }
        print(course_url+str(course_linkid))
        resp = requests.get(course_url+str(course_linkid), headers=header, timeout=2)
        print(resp.text)
        if 'MYSTU/校内办公系统/学分制/网上报修/预约系统' in resp.text:
            response = requests.get(coursesUrl, headers=header, timeout=2)
            if 'MYSTU/校内办公系统/学分制/网上报修/预约系统' in response.text:
                return {'error': 'cookie expired or wrong cookie'}, 401
            else:
                return {'error': 'linkId of course is wrong'}, 400

        if not '找不到数据记录' in resp.text and not '此课程现在不可自助选课' in resp.text:

            position1 = resp.text.find('region-main')
            position2 = resp.text.find('region-pre')
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
            return {'error': 'linkId of course is wrong'}, 400
    except Exception as e:
        print(repr(e))
        return {'error': 'request error'}, 400


def get_folder_files(folder_id, cookies):
    try:
        t0 = time.time()
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Cookie': cookies
        }

        resp = requests.get(folderUrl, headers=header, params={'id': folder_id}, timeout=1.5)
        if 'MYSTU/校内办公系统/学分制/网上报修/预约系统' in resp.text:
            return {'error': 'cookie expired or wrong cookie'}, 401
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
            return {'error': 'linkId of folder is wrong'}, 400
    except Exception as e:
        print(repr(e))
        return {'error': 'request error'}, 400
