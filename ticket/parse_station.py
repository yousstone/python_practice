import re

import requests

from pprint import pprint

url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9028'

response = requests.get(url, verify=False)

stations = re.findall(u'([\u4e00-\u9fa5]+)\|([A-Z]+)', response.text)
# \u4e00-\u9fa5 表示Unicode中汉字的头和尾巴，[]中的值出现一个就行，+表示至少出现一次，
# [\u4e00-\u9fa5]+  表示至少有一个汉字
# [A-Z]+ 表示至少有一个大写字母
pprint(dict(stations), indent=4)
