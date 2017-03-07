from bs4 import BeautifulSoup as BS
import requests
import logging
import prowlpy
import time

logging.basicConfig(format='%(asctime)s %(message)s', filename='tracker.log', level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)

url = "https://order.dominos.com/orderstorage/GetTrackerData?Phone={}"
prowl_api = None

def get_prowl_api(path):
	logging.info('Getting Prowl Api...')
	with open(path) as f:
		prowl_api = readline()
		logging.debug('Prowl Key: {}'.format(prowl_api))

def get_numbers(path):
	phone_list = {}
	logging.info('Getting phone list...')
	with open(path) as f:
		r = f.readlines()
		for line in r:
			phone_list[line.split(":")[0]] = int(line.split(":")[1])
	return phone_list

def order_id_exists(path, order_id):
	logging.info('Checking if order id exists...')
	with open(path) as f:
		r = f.readlines()
		var = list(filter(lambda x: order_id in x, r))
		f.close()
		if not var:
			logging.debug('Order doesn\'t exist...')
			return True
		else:
			logging.debug('Order exists: {}'.format(var[0]))

def store_order(path, order):
        with open(path, "a+") as f:
                f.write("\nName: {}\nNumber: {}\nDate: {}\nTime: {}\nOrder: {}\nMethod: {}\nOrder ID: {}\n\n".format(*order))
                f.close()

def parse_order(page):
	logging.info('Parsing Page...')
	datetime = str(page.find('StartTime').text)
        date, time = datetime.split('T')[0], datetime.split('T')[1]
        method = str(page.find('ServiceMethod').text)
        description = str(page.find('OrderDescription').text)
        _id = str(page.find('OrderID').text)
	r = [date, time, description, method, _id]
	logging.debug('Parsed page: {}'.format(r))

def has_order(status):
	logging.debug('Checking order status: {}'.format(status))
	return status != ""

def post_prowl(event=None, description=None):
	prowl = prowlpy.Prowl(prowl_api)
	prowl.post(application="Domino's Pizza Tracker", event=event, description=description)
	logging.info('Prowl Posted, Event: "{}", Description: "{}"'.format(event, description))

def get_page(name, number):
	try:
		r = requests.get(url.format(str(number)), timeout=5)
		logging.info('{}: {}'.format(r.url, r.status_code))
		if r.status_code == 200:
			return BS(r.content, "xml")
	except requests.exceptions.Timeout:
		logging.warning('Request Timeout for name: {}, number: {}, Passing...'.format(name, str(number)))
		pass
	except:
		logging.critical('Request Failed...')
                pass
		

def main():
	pizza = False
	_path = '/home/ubuntu/python/dominos/'
	get_prowl_api()
	post_prowl(event='Checking Orders...')
	phone_list = get_numbers(_path + 'phone_numbers')
	check_failed = []
	for name, number in phone_list.items():
		page = get_page(name, number)
		if not page:
			check_failed.append('{}: {}'.format(name, number))
			continue
		logging.info("Checking {}, Number: {}".format(name, str(number)))
		if has_order(page.find('OrderStatuses').text):
			parsed_order = [name, str(number)]
			parsed_order += parse_order(page)
			if order_id_exists(_path + 'Order History', parsed_order[-1]):
				store_order(_path + 'Order History', parsed_order)
				event = "{} Ordered Domino's!".format(name)
				description = "Date: {}\nTime: {}\n\nYour homie {} ordered:\n\n{}\nThe method of delivery is: {}".format(parsed_order[2], parsed_order[3], name, parsed_order[4], parsed_order[5])
				post_prowl(event, description)
				pizza = True
		time.sleep(5)
	if not pizza:
		r_str = 'Homies still hungry.\nCheck failed for:\n\n\t'
		logging.info('No orders found...')
		for item in check_failed:
			item += '\n\t'
			r_str += item
		post_prowl(event=r_str)

main()
