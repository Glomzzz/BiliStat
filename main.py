# Author: Glomzzz
# 全是GPT4写的，我只是个搬运工。

import threading
from os import remove
from threading import Lock

import requests
import json

from config import headers


def get_stat(vmid):
    url = f"https://api.bilibili.com/x/relation/stat?vmid={vmid}&jsonp=jsonp"
    response = requests.get(url, headers=headers)
    return response.json()


def read_stat_follower(json):
    return json['data']['follower']


def get_followers_count(vmid):
    return read_stat_follower(get_stat(vmid))


def get_fans(vmid, pn):
    url = f"https://api.bilibili.com/x/relation/fans?vmid={vmid}&pn={pn}&ps=50"
    response = requests.get(url, headers=headers)
    return response.json()


def read_fans(json):
    list = json['data']['list']
    print(len(list))
    # return list.map(lambda x: x['mid'] + " " + x['uname'] + " " + get_followers_count(x['mid']))
    return [f"{x['mid']},{x['uname']}" for x in list]


cache_size = 5000
cache = set()
lock = threading.RLock()

class Progress(object):
    def __init__(self, total):
        self.lock = Lock()
        self.current = 0
        self.total = total

    def add(self, n):
        with self.lock:
            self.current += n

    def get(self):
        return round((self.current / self.total) * 100, 2)


class Task(object):
    # index 从 1 开始，与第一波轮询的pn相同
    def __init__(self, index, tsize, end, output):
        self.index = index
        self.pn = index
        self.tsize = tsize
        self.end = end
        self.output = output

    def start(self):
        print(f"线程 {self.index} 开始执行")
        while self.poll():
            pass
        print(f"线程 {self.index} 执行完毕")

    def poll(self):
        print(f"正在获取第 {self.pn} 页粉丝列表 (每页50人)...")
        fans = read_fans(get_fans(vmid, self.pn))
        print(f"第 {self.pn} 页粉丝列表获取完毕 ( {len(fans)} )，正在处理...")
        lock.acquire()
        if len(cache) >= cache_size:
            print("缓存已满，正在写入文件...")
            release_cache(self.output)
        print(f"第 {self.pn} 页粉丝列表加入缓存...")
        for fan in fans:
            cache.add(fan)
        lock.release()
        self.pn += self.tsize
        return self.pn < self.end

def release_cache(output):
    with open(f"{output}.csv", "a", encoding="UTF-8") as f:
        for fan in cache:
            f.write(f"{fan}\n")
    cache.clear()

def read(vmid, output):
    tsize = 1
    ps = 50
    followers_count = get_followers_count(vmid)

    print(f"{vmid} 粉丝总数：{followers_count}")

    remove(f"{output}.csv")
    with open(f"{output}.csv", "a", encoding="UTF-8") as f:
        f.write(f"mid uname\n")

    time = ((followers_count // ps) // tsize) + 1

    threads = []

    # 生成 tsize 个 线程开始执行任务
    for i in range(1, tsize + 1):
        end = i + time * tsize
        task = Task(i, tsize, end, output)
        threads.append(threading.Thread(target=task.start))

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    release_cache(output)

    print(f"粉丝列表获取完毕, 已写入 {output}.csv")
    print(f"开始获取粉丝的粉丝数")
    with open(f"{output}.csv", "r", encoding="UTF-8") as f:
        remove(f"{output}-followers.csv")
        with open(f"{output}-followers.csv", "a", encoding="UTF-8") as f2:
            f2.write(f"mid uname followers\n")
            lines = f.readlines()
            total = len(lines)
            progress = Progress(total)
            for line in lines[1:]:
                mid, uname = line.split(",")
                uname = uname.strip()
                f2.write(f"{mid},{uname},{get_followers_count(mid)}\n")
                progress.add(1)
                print(f"进度：{progress.get()}%")
    print(f"粉丝的粉丝数获取完毕, 已写入 {output}-followers.csv")
    print("全部任务执行完毕")
if __name__ == '__main__':
    vmid = 263121648
    read(vmid, "Glomzzz")
