import requests
from bs4 import BeautifulSoup
import csv
import os

#Plan:
# 1. We need to define function to get html request
# 2. Need to find out the number of pages
# 3. We need to define function to get content of the page
# 4. parse
# URL = 'https://kolesa.kz/cars/mercedes-benz/almaty/'

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36', 'accept': '*/*'}
FILE = 'kolesa_cars.csv'
HOST = 'https://kolesa.kz'

def get_html(url, params = None):
	r = requests.get(url, headers = HEADERS, params = params)
	return r

def get_number_of_pages(html):
	soup = BeautifulSoup(html, 'lxml')
	try:
		page_count = soup.find('div', class_='pager').find('ul').find_all('span')
		if page_count:
			return int(page_count[-1].get_text())
		else:
			return 1
	except:
		return 1

def get_content(html):
	soup = BeautifulSoup(html, 'lxml')
	content = soup.find_all('div', class_='a-info-side')
	# print(len(content))

	cars = []

	for item in content:

		car_price = item.find('span', class_='price')
		if car_price:
			car_price = car_price.get_text(strip=True).replace('\xa0','').replace('₸','')

		cars.append({
			'title': item.find('span', class_='a-el-info-title').get_text(strip=True),
			'date': item.find('span', class_='date').get_text(),
			'price': car_price,
			'description': item.find('div', class_='a-search-description').get_text(strip=True),
			'city': item.find('div', class_='list-region').get_text(strip=True),
			'link': HOST + item.find('a').get('href')
			})
	return cars

def save_file(items, path):
	with open(path, 'w', newline='') as file:
		writer = csv.writer(file, delimiter=';')
		writer.writerow(['Марка', 'Дата публикации', 'Цена, тенге', 'Краткое описание', 'Город', 'Ссылка',])
		for item in items:
			writer.writerow([item['title'],item['date'],item['price'],item['description'],item['city'],item['link']])


def main():
	URL = input('Введите ссылку для парсинга: ')
	URL = URL.strip()
	html = get_html(URL)
	if html.status_code == 200:
		cars = []
		pages_total = get_number_of_pages(html.text)
		for page in range(1, pages_total+1):
			print(f'Парсинг страницы {page} из {pages_total}...')
			html = get_html(URL, params={'page': page}) #receiving content
			cars.extend(get_content(html.text)) # parsing the received current page and including to cars list
		
		save_file(cars, FILE)
		print(f'Всего {len(cars)} автомобилей')
		os.startfile(FILE)
	else:
		print("Error occured")	

if __name__=="__main__":
	main()