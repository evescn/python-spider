import requests
from pyquery import PyQuery as pq
import pymongo

client = pymongo.MongoClient('10.120.10.198')

db = client.MaoYan

def get_url(url):
    response =  requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

def get_url_datail(response):
    temp_data = pq(response)
    temp_url = temp_data('.nav .navbar li').items()
    for item in temp_url:
        name = item.text()
        url = item('a').attr.href
        if '榜单' in name:
            url = 'https://maoyan.com' + url
            return url

def get_urls(url):
    response = requests.get(url)
    if response.status_code == 200:
        temp_data = pq(response.text)
        data = temp_data('.subnav .navbar li').items()
        for item in data:
            url = item('a').attr.href
            name = item.text()
            if 'board' not in url:
                url = '/board'
            url = 'https://maoyan.com' + url
            yield {
                'url': url,
                'name': name
            }
    else:
        return None

def get_page_datail(response):
    temp_data = pq(response)
    data = temp_data('.main .board-wrapper dd').items()
    for item in data:
        name = item('.name').text()
        actor = item('.star').text()
        pingfen = item('.score .integer ').text() + item('.score .fraction ').text()
        releasetime = item('.releasetime').text()[5:]
        yield {
            'name' : name,
            'actor' : actor,
            'pingfen' : pingfen,
            'releasetime' : releasetime
        }

def sava_to_mongodb(table_name, result):
    try:
        if db[table_name].update({'name': 'table_name'}, {'$set': result}, True):
            print("更新数据库成功：", result['name'])
        elif db[table_name].insert(result):
            print("保存到MongoDB数据库成功：", result)
        else:
            print("保存到MongoDB数据库失败", result)
    except Exception:
        print("出错了")

def main():
    url = 'https://maoyan.com'
    response = get_url(url)
    temp_url = get_url_datail(response)
    urls = get_urls(temp_url)
    for item in urls:
        response = get_url(item['url'])
        temp_data = get_page_datail(response)
        for item_1 in temp_data:
            print(item['name'])
            print(item_1)
            sava_to_mongodb(item['name'], item_1)

if __name__ == '__main__':
    main()