import hashlib
import re
import datetime
import traceback

now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day


def change_datetime_form(string):
    pattern = re.compile('(\d{4})年(\d{1,2})月(\d{1,2})日 (\d{1,2})时(\d{1,2})分:(\d{1,2})秒')
    result = re.findall(pattern, string)
    if len(result) > 0:
        ret = result[0]
        date = '-'.join([ret[0], ret[1], ret[2]])
        time = ':'.join([ret[3], ret[4], ret[5]])

        return date + ' ' + time, date, time


def str2bytes(s):
    md5 = hashlib.md5(bytes(s, encoding="utf8")).hexdigest()
    return md5


def before_n_days(days=1, y=None, m=None, d=None):
    try:
        if y is not None and m is not None and d is not None:
            date = datetime.date(y, m, d)
        else:
            date = now
        before = date + datetime.timedelta(days=-1 * days)
        return True, before.year, before.month, before.day
    except Exception as e:
        print(repr(e))
        return False, None


def dict2string(input_dict):
    try:
        string = ''
        assert isinstance(input_dict, dict)
        for k, v in input_dict.items():
            string = string + k + '=' + v + ';'
        return True, string[:-1]
    except Exception as e:
        print(repr(e))
        return False, None

def string2dict(input_string):
    try:
        if input_string is None:
            return True, None
        elif input_string[-1] == ';':
            input_string = input_string[:-1]
        ret_dict = dict(l.split('=', 1) for l in input_string.split(';'))
        return True, ret_dict
    except Exception as e:
        print(repr(e))
        print(traceback.print_exc())
        return False, None