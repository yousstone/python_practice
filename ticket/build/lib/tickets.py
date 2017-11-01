#!/usr/bin/python3

# coding=utf8
""" 命令行火车票查看器

Usage:
	tickets [-gdtkz] <from> <to> <date>

Options:
	-h,--help     	显示帮助菜单
	-g 	        	高铁
	-d				动车
	-t				特快
	-k				快速
	-z				直达

Example:
	tickets 北京 上海 2017-10-31
	tickets -dg 成都 南京 2017-10-31
"""

from docopt import docopt
from stations import stations
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from prettytable import PrettyTable
from colorama import init, Fore

init()

class TrainsCollection:
	
	header = '车次 车站 时间 历时 一等 二等 软卧 硬卧 硬座 无座'.split()

	def __init__(self, available_trains, options):
		""" 查询到的火车班次集合

		:param available_trains: 一个列表，包含可获得的火车班次，每个火车班次是一个数组

		:param options: 查询的选项，如高铁，动车，etc...
		"""

		self.available_trains = available_trains
		self.options = options

	def _get_duration(self, raw_train):
		duration = raw_train[10].replace(':','小时') + '分'
		if duration.startswith('00'):
			return duration[4:]
		if duration.startswith('0'):
			return duration[1:]
		return duration

	@property
	def trains(self):
		
		code_dict = {v:k for k,v in stations.items()}
		for raw_train in self.available_trains:
			
			raw_train = raw_train.split('|')

			train_no = raw_train[3]
			inital = train_no[0].lower()
			
			if not self.options or inital in self.options:
				train = [
				train_no,
				#6 出发站 7 到达站  8 发车时间 9 到站时间
				# 出发站，终点站
				'\n'.join([Fore.GREEN + code_dict[raw_train[6]] + Fore.RESET,
					   Fore.RED + code_dict[raw_train[7]] + Fore.RESET]),
				# 出发时间，到达时间
				'\n'.join([Fore.GREEN + raw_train[8] + Fore.RESET,
					   Fore.RED + raw_train[9] + Fore.RESET]),
				self._get_duration(raw_train),
				raw_train[31] or '--', # 一等座
				raw_train[30] or '--', # 二等座
				raw_train[23] or '--', # 软卧
				raw_train[28] or '--', # 硬卧
				raw_train[29] or '--', # 硬座
				raw_train[26] or '--',  # 无座
				]
				yield train

	def pretty_print(self):
		pt = PrettyTable()
		pt._set_field_names(self.header)
		for train in self.trains:
			pt.add_row(train)
		print(pt)

  
def cli():

	'''command-line interface'''

	arguments = docopt(__doc__)
	from_station = stations.get(arguments['<from>'])
	to_station = stations[arguments['<to>']]
	date = arguments['<date>']

	# 构建URL
	url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(date,from_station,to_station)
	# 禁用安全请求警告,避免安全性的Warning
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

	# 添加verify=False参数不验证证书
	r = requests.get(url, verify=False)
	
	# 车次类型合集转成字符串	
	options = ''.join([key for key,value in arguments.items() if value is True])

	available_trains = r.json()['data']['result']
	TrainsCollection(available_trains, options).pretty_print()

if __name__ == '__main__':
	cli()


