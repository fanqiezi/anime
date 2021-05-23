from datetime import datetime
from functools import partial
import lxml.etree
from multiprocessing import Pool
import os
import requests
from faker import Factory
import tkinter as tk
from numpy import random
from time import sleep


headers = {
    'Cookie': 'qovlrlastsearchtime=1620095214; fz_history=%5B%7B%22name%22%3A%22%u5200%u5251%u795E%u57DF%u5916%u4F20'
              '%20Gun%20Gale%20Online%uFF08%u7B2C1%u96C6%uFF09%22%2C%22link%22%3A%22/anime/930/1/%22%7D%2C%7B%22name'
              '%22%3A%22%u732B%u54AAdays%uFF08%u7B2C1%u96C6%uFF09%22%2C%22link%22%3A%22/anime/2636/1/%22%7D%2C%7B'
              '%22name%22%3A%22Citrus%uFF5E%u67D1%u6A58%u5473%u9999%u6C14%uFF08%u7B2C1%u96C6%uFF09%22%2C%22link%22%3A'
              '%22/anime/998/1/%22%7D%2C%7B%22name%22%3A%22%u5F71%u4E4B%u8BD7%uFF08%u7B2C48.5%u96C6%uFF09%22%2C'
              '%22link%22%3A%22/anime/3055/50/%22%7D%2C%7B%22name%22%3A%22%u65E0%u804C%u8F6C%u751F%7E%u5230%u4E86'
              '%u5F02%u4E16%u754C%u5C31%u62FF%u51FA%u771F%u672C%u4E8B%7E%uFF08%u7B2C1%u96C6%uFF09%22%2C%22link%22%3A'
              '%22/anime/804/1/%22%7D%2C%7B%22name%22%3A%22%u8F7B%u97F3%u5C11%u5973%u5267%u573A%u7248%uFF08%u51681'
              '%u96C6%uFF09%22%2C%22link%22%3A%22/anime/3794/1/%22%7D%2C%7B%22name%22%3A%22%u5243%u987B%u3002%u7136'
              '%u540E%u6361%u5230%u5973%u9AD8%u4E2D%u751F%uFF08%u7B2C2%u96C6%uFF09%22%2C%22link%22%3A%22/anime/3373/2'
              '/%22%7D%2C%7B%22name%22%3A%22%u6D77%u8D3C%u738B%uFF08%u7B2C971%u96C6%uFF09%22%2C%22link%22%3A%22/anime'
              '/241/971/%22%7D%5D',
    'User-Agent': Factory.create().user_agent()  # 生成随机ua
}

headers2 = {
    'Referer': 'http://www.milimili.cc/',
    'Upgrade-Insecure-Requests': '1'
}

left_url = 'http://www.milimili.cc'

FOLDER_NAME = "动漫"  # 文件夹名

FREQUENCY_MAX = 5  # 重新请求次数


def get_type_url(w, word):
    frequency = 1
    while frequency < FREQUENCY_MAX:
        try:
            url = 'http://www.milimili.cc/e/search/index.php'
            data = {'show': 'title,ftitle', 'tbname': 'movie', 'tempid': '1', 'keyboard': word}
            print("尝试第{0}次请求 {1}".format(frequency, url))
            response = requests.post(url, data, timeout=10)
            response.encoding = 'utf-8'
            response = lxml.etree.HTML(response.text)
            divs = response.xpath('/html/body/div[4]/div[2]/div[1]/ul/li')
            titles = []
            numbers = []
            type_urls = []
            for div in divs:
                titles.append(div.xpath('./h2/a/@title')[0])
                if len(div.xpath('./span[1]/font/text()')):
                    numbers.append(div.xpath('./span[1]/font/text()')[0])
                else:
                    numbers.append(None)
                type_urls.append(div.xpath('./h2/a/@href')[0])
            return titles, numbers, type_urls
        except Exception as e:
            tk.Label(w, text="下载失败 {0}".format(e)).place(x=5, y=470, anchor="nw")
            frequency += 1
            tk.Label(w, text="尝试第{}次请求".format(frequency)).place(x=5, y=450, anchor="nw")
            sleep(5)


def get_num_url(w, type_url):
    frequency = 1
    while frequency <= FREQUENCY_MAX:
        try:
            print("尝试第{0}次请求 {1}".format(frequency, left_url + type_url))
            response = requests.get(left_url + type_url, headers, timeout=10)
            response.encoding = 'utf-8'
            response = lxml.etree.HTML(response.text)
            number_urls = response.xpath('//*[@id="main0"]/div/ul/li/a/@href')
            texts = response.xpath('//*[@id="main0"]/div/ul/li/a/text()')
            urls = []
            for number_url in number_urls:
                number_url = left_url + number_url
                urls.append(number_url)
            return urls, texts
        except Exception as e:
            tk.Label(w, text="下载失败 {0}".format(e)).place(x=5, y=470, anchor="nw")
            frequency += 1
            tk.Label(w, text="尝试第{}次请求".format(frequency)).place(x=5, y=450, anchor="nw")
            sleep(5)


def get_media_url(w, number_url):
    frequency = 1
    while frequency < FREQUENCY_MAX:
        try:
            print("拼接 {}".format(number_url))
            aid = number_url.split("/")[4]
            pid = number_url.split("/")[5]
            two_media_url = "http://www.milimili.cc/e/action/player_i.php?id=" + aid + "&pid=" + pid + "&playid=&" + str(
                round(random.uniform(0, 1), 16))  # 设置范围0-1精度16位的随机数
            print("尝试第{0}次请求 {1}".format(frequency, two_media_url))
            response = requests.get(two_media_url, headers2, timeout=10)
            response.encoding = 'utf-8'
            response = lxml.etree.HTML(response.text)
            media_url = response.xpath('//iframe/@src')[0].split('=')[-1]
            return media_url
        except Exception as e:
            tk.Label(w, text="下载失败 {0}".format(e)).place(x=5, y=470, anchor="nw")
            frequency += 1
            tk.Label(w, text="尝试第{}次请求".format(frequency)).place(x=5, y=450, anchor="nw")
            sleep(5)


def download_mp4(media_url, title, text):
    path = os.getcwd()
    if not os.path.exists(path + '\\' + FOLDER_NAME):
        os.mkdir(path + '\\' + FOLDER_NAME)
    if not os.path.exists(path + '\\' + FOLDER_NAME + '\\' + title):
        os.mkdir(path + '\\' + FOLDER_NAME + '\\' + title)
    print("请求 {}".format(media_url))
    media = requests.get(url=media_url, timeout=10)
    with open(path + '\\' + FOLDER_NAME + '\\' + title + '\\' + "{}".format(str(text)) + '.mp4', 'wb') as f:
        f.write(media.content)
        f.flush()
        f.close()


def ok1(w, lb2, number_urls, texts, title):
    try:
        tk.Label(w, text="", width=200).place(x=5, y=470, anchor="nw")
        num = int(lb2.get(lb2.curselection()).split()[0])
        media_url = get_media_url(w, number_urls[num - 1])
        text = texts[num - 1]
        if media_url.split('.')[-1] == 'mp4':
            tk.Label(w, text="{0} 开始下载...".format(text)).place(x=5, y=470, anchor="nw")
            print('{0} 开始下载...'.format(text))
            start_time = datetime.now()
            download_mp4(media_url, title, text)
            end_time = datetime.now()
            tk.Label(w, text="{0} 下载完成\t耗时:{1}".format(text, end_time - start_time)).place(x=5, y=470,
                                                                                                     anchor="nw")
            print('{0} 下载完成\n耗时:{1}'.format(text, end_time - start_time))
        else:
            raise Exception("不是MP4视频")
    except Exception as e:
        tk.Label(w, text="下载失败 {0}".format(e)).place(x=5, y=470, anchor="nw")
        print(e, '\n下载失败')


def ok2(w, number_urls, Entry1, Entry2, texts, title):
    try:
        tk.Label(w, text="", width=200).place(x=5, y=470, anchor="nw")
        start = int(Entry1.get())
        end = int(Entry2.get())
        start_time = datetime.now()
        pool = Pool(end - start + 1)
        for num in range(start, end + 1):
            media_url = get_media_url(w, number_urls[num - 1])
            text = texts[num - 1]
            if media_url.split('.')[-1] == 'mp4':
                tk.Label(w, text="{0} 开始下载...".format(text)).place(x=5, y=470, anchor="nw")
                print('{0} 开始下载...'.format(text))
                pool.apply_async(download_mp4, (media_url, title, text))
                print('{0} 下载完成'.format(text))
            else:
                raise Exception("不是MP4视频")
        pool.close()
        pool.join()
        end_time = datetime.now()
        tk.Label(w, text="全部下载完成\t耗时:{0}".format(end_time - start_time)).place(x=300, y=470, anchor="nw")
        print('全部下载完成\n耗时:{0}'.format(end_time - start_time))
    except Exception as e:
        tk.Label(w, text="下载失败 {0}".format(e)).place(x=5, y=470, anchor="nw")
        print(e, '\n下载失败')


def chioce_number(w, lb2, number_urls, texts, title):
    tk.Label(w, text="", width=200).place(x=260, y=45, anchor="nw")
    tk.Label(w, text="选择下载第几集:").place(x=260, y=45, anchor="nw")
    tk.Button(w, text="确定", command=lambda: ok1(w, lb2, number_urls, texts, title)).place(x=450, y=40, anchor="nw")


def chioce_number2(w, number_urls, texts, title):
    tk.Label(w, text="", width=200).place(x=260, y=45, anchor="nw")
    tk.Label(w, text="输入下载第").place(x=260, y=45, anchor="nw")
    start = tk.Entry(w, width=3)
    start.place(x=325, y=45, anchor="nw")
    tk.Label(w, text="到第").place(x=350, y=45, anchor="nw")
    end = tk.Entry(w, width=3)
    end.place(x=380, y=45, anchor="nw")
    tk.Label(w, text="集(序号)").place(x=400, y=45, anchor="nw")
    tk.Button(w, text="确定", command=lambda: ok2(w, number_urls, start, end, texts, title)).place(x=450, y=40, anchor="nw")


def chioce_opton(w, lb, titles, type_urls):
    type_index = int(lb.get(lb.curselection()).split()[0])
    title = titles[type_index - 1]
    number_urls, texts = get_num_url(w, type_urls[type_index - 1])
    lb2 = tk.Listbox(w, bg="pink", width=34, height=18)
    lb2.place(x=255, y=120, anchor="nw")
    for i in range(len(texts)):
        item = "{0} {1}".format(i + 1, texts[i])
        lb2.insert(tk.END, item)
    tk.Label(w, text="选择下载方式:").place(x=260, y=50, anchor="nw")
    tk.Button(w, text="单集下载", command=lambda: chioce_number(w, lb2, number_urls, texts, title)).place(x=345, y=5,
                                                                                                   anchor="nw")
    tk.Button(w, text="批量下载", command=lambda: chioce_number2(w, number_urls, texts, title)).place(x=405, y=5, anchor="nw")


def search(w, word):
    tk.Label(w, text="", width=200).place(x=260, y=85, anchor="nw")
    tk.Label(w, text="正在搜索...").place(x=5, y=85, anchor="nw")
    word = word.get()
    titles, numbers, type_urls = get_type_url(w, word)
    if len(type_urls):
        tk.Label(w, text="", width=200).place(x=5, y=85, anchor="nw")
        lb = tk.Listbox(w, bg="pink", width=34, height=18)
        lb.place(x=5, y=120, anchor="nw")
        tk.Label(w, text="找到以下资源 选择下载哪一部").place(x=5, y=90, anchor="nw")
        for i in range(len(type_urls)):
            item = "{0}  {1} {2}".format(i + 1, titles[i], numbers[i])
            lb.insert(tk.END, item)
        tk.Button(w, text="确定", command=lambda: chioce_opton(w, lb, titles, type_urls)).place(x=220, y=80,
                                                                                           anchor="nw")  # 使用匿名函数传递参数
    else:
        tk.Label(w, text="", width=20).place(x=5, y=85, anchor="nw")
        tk.Label(w, text="没有找到任何记录").place(x=5, y=85, anchor="nw")
        print('没有找到任何记录')




