from datetime import datetime
from functools import partial
import lxml.etree
from multiprocessing import Pool
import os
import requests
from faker import Factory
import tkinter as tk


FOLDER_NAME = "动漫"

headers = {
    'user-agent': Factory.create().user_agent(),  # 生成随机ua
    'referer': 'https://www.tmdm.tv/search/%E5%93%86%E5%95%A6A%E6%A2%A6/?page=1'
}


def get_url(work):
    url = 'https://www.tmdm.tv/search/{0}/'.format(work)
    return url


def get_type_url(url):
    response = requests.get(url=url, headers=headers)
    response.encoding = 'utf-8'
    response = lxml.etree.HTML(response.text)
    divs = response.xpath('//div[@class="lpic"]/ul/li')
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


def get_num_url(type_url):
    response = requests.get(url=type_url, headers=headers)
    response.encoding = 'utf-8'
    response = lxml.etree.HTML(response.text)
    number_urls = response.xpath('//div[@class="movurl"]/ul/li/a/@href')
    texts = response.xpath('//div[@class="movurl"]/ul/li/a/text()')
    urls = []
    for number_url in number_urls:
        number_url = type_url + number_url
        urls.append(number_url)
    return urls, texts


def get_point_media_url(number_url):
    left_url = 'https://player.tmdm.tv/disp.php?vid='
    response = requests.get(url=number_url, headers=headers)
    response.encoding = 'utf-8'
    response = lxml.etree.HTML(response.text)
    point_media_url = response.xpath('/html/body/div[2]/div[5]/div/@data-vid')[0]
    point_media_url = left_url + point_media_url
    return point_media_url


def get_media_url(point_media_url):
    response = requests.get(url=point_media_url, headers=headers)
    response.encoding = 'utf-8'
    response = lxml.etree.HTML(response.text)
    media_url = response.xpath('/html/body/script/text()')[0].split('url')[1].split('"')[1]
    return media_url


def download_mp4(media_url, title, num):
    path = os.getcwd()
    if not os.path.exists(path + '\\' + FOLDER_NAME):
        os.mkdir(path + '\\' + FOLDER_NAME)
    if not os.path.exists(path + '\\' + FOLDER_NAME + '\\' + title):
        os.mkdir(path + '\\' + FOLDER_NAME + '\\' + title)
    media = requests.get(url=media_url, headers=headers)
    with open(path + '\\' + FOLDER_NAME + '\\' + title + '\\' + str(num) + '.mp4', 'wb') as f:
        f.write(media.content)
        f.flush()
        f.close()


def get_ts_url(m3u8_url):
    left_url = m3u8_url[:m3u8_url.rfind('/')] + '/'
    text = requests.get(url=m3u8_url, headers=headers).text
    texts = text.split('\n')
    ts_urls = []
    for i in range(len(texts)):
        if texts[i].endswith(".ts"):
            ts_urls.append(left_url + texts[i])
        else:
            continue
    return ts_urls


def download_ts(ts_urls, title, num):
    path = os.getcwd()
    if not os.path.exists(path + '\\动漫'):
        os.mkdir(path + '\\动漫')
    if not os.path.exists(path + '\\动漫\\' + title):
        os.mkdir(path + '\\动漫\\' + title)
    ts = requests.get(url=ts_urls, headers=headers)
    with open(path + '\\动漫\\' + title + '\\' + "第{}集".format(str(num)) + '.ts', 'ab') as f:
        f.write(ts.content)
        f.flush()
        f.close()


def ok1(w, lb2, number_urls, texts, title):
    tk.Label(w, text="", width=200).place(x=5, y=470, anchor="nw")
    num = int(lb2.get(lb2.curselection()).split()[0])
    point_media_url = get_point_media_url(number_urls[num - 1])
    media_url = get_media_url(point_media_url)
    try:
        if media_url.split('.')[-1] == 'mp4':
            tk.Label(w, text="{0} 开始下载...".format(texts[num - 1])).place(x=5, y=470, anchor="nw")
            print('{0} 开始下载...'.format(texts[num - 1]))
            start_time = datetime.now()
            pool = Pool(os.cpu_count())
            pool.apply_async(partial(download_mp4, w, title=title, num=texts[num - 1]), (media_url,))
            pool.close()
            pool.join()
            end_time = datetime.now()
            tk.Label(w, text="{0} 下载完成\t耗时:{1}".format(texts[num - 1], end_time - start_time)).place(x=5, y=470,
                                                                                                     anchor="nw")
            print('{0} 下载完成\n耗时:{1}'.format(texts[num - 1], end_time - start_time))
        elif media_url.split('.')[-1] == 'm3u8':
            if media_url.split('/')[-1] == 'index.m3u8':
                media_url = media_url[:media_url.rfind('/')] + '/' + '1000k/hls/index.m3u8'
            ts_urls = get_ts_url(media_url)
            tk.Label(w, text="{0} 开始下载...".format(texts[num - 1])).place(x=5, y=470, anchor="nw")
            print('{0} 开始下载...'.format(texts[num - 1]))
            start_time = datetime.now()
            pool = Pool(processes=os.cpu_count())
            for ts_url in ts_urls:
                pool.apply(partial(download_ts, w, title=title, num=texts[num - 1]), (ts_url,))
            pool.close()
            pool.join()
            end_time = datetime.now()
            tk.Label(w, text="{0} 下载完成\t耗时:{1}".format(texts[num - 1], end_time - start_time)).place(x=5, y=470,
                                                                                                     anchor="nw")
            print('{0} 下载完成\n耗时:{1}'.format(texts[num - 1], end_time - start_time))
        else:
            raise Exception("不是m3u8视频")
    except Exception as e:
        tk.Label(w, text="下载失败 {0}".format(e)).place(x=5, y=470, anchor="nw")
        print(e, '\n下载失败')


def ok2(w, number_urls, Entry1, Entry2, texts, title):
    tk.Label(w, text="", width=200).place(x=5, y=470, anchor="nw")
    start = int(Entry1.get())
    end = int(Entry2.get())
    try:
        start_time = datetime.now()
        pool = Pool(processes=os.cpu_count())
        for num in range(start, end + 1):
            point_media_url = get_point_media_url(number_urls[num - 1])
            media_url = get_media_url(point_media_url)
            if media_url.split('.')[-1] == 'mp4':
                tk.Label(w, text="{0} 开始下载...".format(texts[num - 1])).place(x=5, y=470, anchor="nw")
                tk.Label(w, text="", width=200).place(x=260, y=45, anchor="nw")
                start_time_sub = datetime.now()
                pool = Pool(os.cpu_count())
                pool.apply_async(partial(download_mp4, w, title=title, num=texts[num - 1]), (media_url,))
                end_time_sub = datetime.now()
                tk.Label(w, text="{0} 下载完成\t耗时:{1}".format(texts[num - 1], end_time_sub - start_time_sub)).place(x=5,
                                                                                                                 y=470,
                                                                                                                 anchor="nw")
            elif media_url.split('.')[-1] == 'm3u8':
                if media_url.split('/')[-1] == 'index.m3u8':
                    media_url = media_url[:media_url.rfind('/')] + '/' + '1000k/hls/index.m3u8'
                ts_urls = get_ts_url(media_url)
                tk.Label(w, text="{0} 开始下载...".format(texts[num - 1])).place(x=5, y=470, anchor="nw")
                print('{0} 开始下载...'.format(texts[num - 1]))
                start_time_sub = datetime.now()
                pool = Pool(processes=os.cpu_count())
                for ts_url in ts_urls:
                    pool.apply(partial(download_ts, w, title=title, num=texts[num - 1]), (ts_url,))
                end_time_sub = datetime.now()
                print('{0} 下载完成\n耗时:{1}'.format(texts[num - 1], end_time_sub - start_time_sub))
                tk.Label(w, text="{0} 下载完成\t耗时:{1}".format(texts[num - 1], end_time_sub - start_time_sub)).place(x=5,
                                                                                                                 y=470,
                                                                                                                 anchor="nw")
            else:
                raise Exception("不是m3u8或mp4视频")
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
    tk.Button(w, text="确定", command=lambda: ok1(w, lb2, number_urls, texts, title)).place(x=425, y=40, anchor="nw")


def chioce_number2(w, number_urls, texts, title):
    tk.Label(w, text="", width=200).place(x=260, y=45, anchor="nw")
    tk.Label(w, text="输入下载第").place(x=260, y=45, anchor="nw")
    start = tk.Entry(w, width=3)
    start.place(x=325, y=45, anchor="nw")
    tk.Label(w, text="到第").place(x=350, y=45, anchor="nw")
    end = tk.Entry(w, width=3)
    end.place(x=380, y=45, anchor="nw")
    tk.Label(w, text="集").place(x=400, y=45, anchor="nw")
    tk.Button(w, text="确定", command=lambda: ok2(w, number_urls, start, end, texts, title)).place(x=425, y=40, anchor="nw")


def chioce_opton(w, lb, titles, type_urls):
    type_index = int(lb.get(lb.curselection()).split()[0])
    title = titles[type_index - 1]
    number_urls, texts = get_num_url(type_urls[type_index - 1])
    lb2 = tk.Listbox(w, bg="pink", width=34, height=18)
    lb2.place(x=255, y=120, anchor="nw")
    for i in range(len(texts)):
        item = "{0} {1}".format(i + 1, texts[i])
        lb2.insert(tk.END, item)
    tk.Label(w, text="选择下载方式:").place(x=260, y=10, anchor="nw")
    tk.Button(w, text="单集下载", command=lambda: chioce_number(w, lb2, number_urls, texts, title)).place(x=345, y=5,
                                                                                                   anchor="nw")
    tk.Button(w, text="批量下载", command=lambda: chioce_number2(w, number_urls, texts, title)).place(x=405, y=5, anchor="nw")


def search(w, work):
    tk.Label(w, text="", width=200).place(x=260, y=85, anchor="nw")
    tk.Label(w, text="正在搜索...").place(x=5, y=85, anchor="nw")
    work = work.get()
    url = get_url(work)
    titles, numbers, type_urls = get_type_url(url)
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


def exit_w(w):
    w.destroy()



