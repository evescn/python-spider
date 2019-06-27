import requests
from pyquery import PyQuery as pq
import pymongo
from multiprocessing import Pool
import re

client = pymongo.MongoClient('192.168.0.100')
db = client['MaoYan']

def get_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

def get_page_datail(response):
    temp_data = pq(response)
    list_data = temp_data('.container .cinemas-list .cinema-cell').items()
    for item in list_data:
        cinemas = item('.cinema-name').text()
        address = item('.cinema-address').text()[3:]
        cinemas_play_url = 'https://maoyan.com' + item('.cinema-info a').attr.href
        # print(cinemas_play_url)
        # print(cinemaname)
        # print(address)
        yield {
            'cinemas': cinemas,
            'address': address,
            'cinemas_play_url': cinemas_play_url
        }

def get_cinemas_page_datail(response):
    temp_data = pq(response)
    movie_data = temp_data('.container .show-list').items()
    for item in movie_data:
        # print(item)
        movie_name = item('.movie-name').text()
        movie_score = item('.score').text()
        data = re.split(r'[:\n]', item('.movie-desc').text())
        # print(data)
        movie_time = None
        movie_type = None
        movie_actor = None
        data_len = len(data)
        if data_len < 4:
            movie_time = data[1]
        elif data_len < 6:
            movie_time = data[1]
            movie_type = data[3]
        else:
            movie_time = data[1]
            movie_type = data[3]
            movie_actor = data[5]

        yield {
            'movie_name': movie_name,
            'movie_score': movie_score,
            'movie_time': movie_time,
            'movie_type': movie_type,
            'movie_actor': movie_actor
        }

def get_time_page_datail(response):
    temp_data = pq(response)
    time_data = temp_data('.container .show-list .show-date').items()
    for item in time_data:
        # print(item)
        time = item('.date-item').text()
        # print(time)
        if '今天'not in time:
            time = re.split(r' ', time)
            num = len(time)/2
            print(time)
            key = 0
            while key <= len(time):
                yield {
                    'time': time[key+1]
                }
                key = key + 2
    return None

def sava_to_mongodb_cinemas(table_name, result):
    try:
        if db[table_name].update_one({'cinemas': result['cinemas']}, {'$set': result}, True):
            print("更新数据库成功：", result['cinemas'])
        elif db[table_name].insert_one(result):
            print("保存到MongoDB数据库成功：", result)
        else:
            print("保存到MongoDB数据库失败", result)
    except Exception:
        print("出错了")

def sava_to_mongodb_movie(table_name, result):
    try:
        if db[table_name].update_one({'movie_name': result['movie_name'], 'cinemas_address_id': result['cinemas_address_id']}, {'$set': result}, True):
            print("更新数据库成功：", result['movie_name'])
        elif db[table_name].insert_one(result):
            print("保存到MongoDB数据库成功：", result)
        else:
            print("保存到MongoDB数据库失败", result)
    except Exception:
        print("出错了")

def main(offset):
    url = 'https://maoyan.com/cinemas?offset=' + str(offset)
    # print(url)
    response = get_page(url)
    cinemas_address = get_page_datail(response)
    for item in cinemas_address:
        # print(item)
        sava_to_mongodb_cinemas('cinemas_address', item)
        temp_repsonse = get_page(item['cinemas_play_url'])
        movie_info = get_cinemas_page_datail(temp_repsonse)
        for item_movie in movie_info:
            # print(item_movie)
            ObjectId = db['cinemas_address'].find({'cinemas': item['cinemas']}, {'item': 1, 'status': 1})
            for item_id in ObjectId:
                # print(item_id)
                item_movie['cinemas_address_id'] = str(item_id['_id'])
                print(item_movie)
                sava_to_mongodb_movie('movie_info', item_movie)
        time_info = get_time_page_datail(temp_repsonse)
        # print(time_info)
        for item_time in time_info:
            print(item_time)

if __name__ == '__main__':
    # pool = Pool()
    # groups = [x * 12 for x in range(0, 19)]
    # pool.map(main, groups)
    # pool.close()
    # pool.join()
    main(0)