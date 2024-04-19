import joblib
import os
import re
from bs4 import BeautifulSoup
from threading import Lock
import pandas as pd
from time import sleep
import requests
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

print_lock = Lock()

def split_series(series, n):

    total_elements = len(series)
    elements_per_partition, remainder = divmod(total_elements, n)

    start = 0
    partitions = []

    for i in range(n):
        end = start + elements_per_partition + (1 if i < remainder else 0)
        partition = series[start:end]
        partitions.append(partition)
        start = end

    return partitions


def scrape_data(uid, time_range, header):
    global weibo
    global failed
    global tasklength
    global finished

    constraint = '&hasori=1&hasret=1&hastext=1&haspic=1&hasvideo=1&hasmusic=1'
    for time_ in time_range:
        try:
            page = 1
            url = f'https://weibo.com/ajax/statuses/searchProfile?uid={uid}&page={page}&starttime={int(time_.timestamp())}&endtime={int(time_.timestamp()) + 86400}{constraint}'
            not_connected = True
            tried = 0
            while not_connected and tried < 3:
                try:
                    response = requests.get(url, headers=header)
                    not_connected = False
                except:
                    tried += 1
                    sleep(20)
            if tried >= 3:
                raise ValueError("....")

            if response.status_code != 200:
                raise ValueError("....")

            data = json.loads(response.content.decode('utf-8'))

            temp = []
            for blog in data['data']['list']:
                temp.append({'用户名': blog['user']['screen_name'],
                             '发表时间': blog['created_at'],
                             '发表内容': blog['text_raw'].replace('\u200b\u200b\u200b', '')})

            this_page_collected = len(temp)
            while this_page_collected == 20:
                this_page = []
                page += 1
                url = url.replace(f'page={page-1}', f'page={page}')
                sleep(5)
                not_connected = True
                tried = 0
                while not_connected and tried < 3:
                    try:
                        response = requests.get(url, headers=header)
                        not_connected = False
                    except:
                        tried += 1
                        sleep(20)

                if response.status_code != 200:
                    raise ValueError("....")

                data = json.loads(response.content.decode('utf-8'))

                for blog in data['data']['list']:
                    this_page.append({'用户名': blog['user']['screen_name'],
                                 '发表时间': blog['created_at'],
                                 '发表内容': blog['text_raw'].replace('\u200b\u200b\u200b', '')})
                temp += this_page
                this_page_collected = len(this_page)

            weibo += temp
            finished += 1
            with print_lock:
                print(f'\033[92mFinished\033[0m : {finished}/{tasklength} \033[91mFailed\033[0m : {len(failed)}', end='\r')
            sleep(5)

        except:
            finished += 1
            failed.append(time_)
            with print_lock:
                print(f'\033[92mFinished\033[0m : {finished}/{tasklength} \033[91mFailed\033[0m : {len(failed)}', end='\r')
            sleep(10)
            
    return None


def get_weibo_parallel(uid, splitted, headers_list):
    global weibo
    global failed
    global finished
    global tasklength

    headers_count = len(headers_list)

    with ThreadPoolExecutor(max_workers=headers_count) as executor:
        futures = [executor.submit(scrape_data, uid, splitted[i], headers_list[i]) for i in range(headers_count)]

        for future in as_completed(futures):
            future.result()
            
    print(f'\033[92mFinished\033[0m : {finished}/{tasklength} \033[91mFailed\033[0m : {len(failed)}')

    return None

if __name__ == '__main__':
    # setting up headers--------------------------------------------------------------------
    headers = []
    
    for file in os.listdir('./headers/'):
        headers.append(joblib.load('./headers/' + file))
    #-----------------------------------------------------------------------------------------
    
    weibo = []
    failed = []
    
    # setting up parameters---------------------------------------------------------------
    UID = 2813700891
    user_name = '微博基金'
    begin_time = '2024-01-21'
    end_time = '2024-01-31'
    full_time_range = pd.date_range(begin_time, end_time)
    #----------------------------------------------------------------------------------------
    
    splitted = split_series(full_time_range, len(headers))
    
    tasklength = len(full_time_range)
    finished = 0
    
    # collecting
    start = datetime.now()
    get_weibo_parallel(UID, splitted, headers)
    end = datetime.now()
    print(end-start, ' '.ljust(60))
    
    weibo = pd.DataFrame(weibo)
    # weibo['发表时间'] = pd.to_datetime(weibo['发表时间'], format="%a %b %d %H:%M:%S %z %Y")
    # weibo.sort_values(by='发表时间').to_csv(f'./data/{user_name}.csv', index=False)
