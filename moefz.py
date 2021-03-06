from datetime import datetime
import lxml.etree
from multiprocessing import Pool
import os
import requests
from faker import Factory
import tkinter as tk


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'G3xE_2132_saltkey=Tq1uTboF; G3xE_2132_lastvisit=1620022919; '
              'UM_distinctid=179311b3861240-0f84ee25708c62-d7e1739-144000-179311b38621d2; '
              'G3xE_2132_visitedfid=44D91D54; G3xE_2132_forum_lastvisit=D_91_1620026835D_44_1620029052; '
              'CNZZDATA1274241190=554679791-1620026538-%7C1620177430; G3xE_2132_sid=loU8OU; G3xE_2132_sendmail=1; '
              'G3xE_2132_lastact=1620182740%09search.php%09forum',
    'Host': 'www.moefz.cc',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': Factory.create().user_agent()  # 生成随机ua
}

left_url = 'http://www.moefz.cc/'

FOLDER_NAME = "动漫"  # 文件夹名


def get_type_url(w, word):
    try:
        url = 'http://www.moefz.cc/search.php?mod=forum'
        data = {'formhash': 'a3c1a919',
                'srchtxt': word,
                'searchsubmit': 'yes'}
        response = requests.post(url=url, data=data, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        print('请求 {}'.format(url))
        response = lxml.etree.HTML(response.text)
        divs = response.xpath('//*[@id="threadlist"]/ul/li')
        titles = []
        type_urls = []
        title = ''
        for div in divs:
            titles_1 = div.xpath('./h3/a//text()')
            for title_1 in range(len(titles_1)):
                title += titles_1[title_1]
            titles.append(title)
            title = ''
            type_urls.append(left_url + div.xpath('./h3/a/@href')[0])
        return titles, type_urls
    except Exception as e:
        tk.Label(w, text="下载失败 {0}".format(e)).place(x=5, y=470, anchor="nw")


def get_num_url(w, type_url):
    try:
        print('请求 {}'.format(type_url))
        response = requests.get(type_url, timeout=10)
        response.encoding = 'utf-8'
        html = response.text
        url_1 = html.split('video":"')
        urls = []
        for d in url_1:
            text = d.split('"}')
            for t in text:
                if t.endswith('.mp4'):
                    urls.append(t)
        media_urls = []
        for url in urls:
            media_urls.append(url.replace(r'\/', '/'))
        texts = []
        texts_1 = html.split(':')
        for text_1 in texts_1:
            if text_1.endswith(',"pre"'):
                text_1 = text_1.replace(',"pre"', '')
                texts.append("第{}集".format(int(text_1) + 1))
        return media_urls, texts
    except Exception as e:
        tk.Label(w, text="下载失败 {0}".format(e)).place(x=5, y=470, anchor="nw")


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


def ok1(w, lb2, media_urls, texts, title):
    try:
        tk.Label(w, text="", width=200, height=30).place(x=5, y=460, anchor="nw")
        num = int(lb2.get(lb2.curselection()).split()[0])
        media_url = media_urls[num - 1]
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


def ok2(w, media_urls, Entry1, Entry2, texts, title):
    try:
        tk.Label(w, text="", width=200, height=30).place(x=5, y=460, anchor="nw")
        start = int(Entry1.get())
        end = int(Entry2.get())
        start_time = datetime.now()
        pool = Pool(end - start + 1)
        for num in range(start, end + 1):
            media_url = media_urls[num - 1]
            text = texts[num - 1]
            if media_url.split('.')[-1] == 'mp4':
                print('{0} 开始下载...'.format(text))
                tk.Label(w, text="{0} 开始下载...".format(text)).place(x=5, y=470, anchor="nw")
                print(media_url, title, text)
                pool.apply_async(download_mp4, (media_url, title, text))    # 多进程异步下载
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


def chioce_number(w, lb2, media_urls, texts, title):
    tk.Label(w, text="选择下载第几集:").place(x=260, y=45, anchor="nw")
    tk.Button(w, text="确定", command=lambda: ok1(w, lb2, media_urls, texts, title)).place(x=450, y=40, anchor="nw")


def chioce_number2(w, media_urls, texts, title):
    tk.Label(w, text="输入下载第").place(x=260, y=45, anchor="nw")
    start = tk.Entry(w, width=3)
    start.place(x=325, y=45, anchor="nw")
    tk.Label(w, text="到第").place(x=350, y=45, anchor="nw")
    end = tk.Entry(w, width=3)
    end.place(x=380, y=45, anchor="nw")
    tk.Label(w, text="集(序号)").place(x=400, y=45, anchor="nw")
    tk.Button(w, text="确定", command=lambda: ok2(w, media_urls, start, end, texts, title)).place(x=450, y=40, anchor="nw")


def chioce_opton(w, lb, titles, type_urls):
    type_index = int(lb.get(lb.curselection()).split()[0])
    title = titles[type_index - 1]
    media_urls, texts = get_num_url(w, type_urls[type_index - 1])
    lb2 = tk.Listbox(w, bg="pink", width=34, height=18)
    lb2.place(x=255, y=120, anchor="nw")
    for i in range(len(texts)):
        item = "{0} {1}".format(i + 1, texts[i])
        lb2.insert(tk.END, item)
    if not media_urls:
        lb2.insert(tk.END, "无在线资源 相关资料↓")
        lb2.insert(tk.END, type_urls[type_index - 1])
    tk.Label(w, text="选择下载方式:").place(x=260, y=10, anchor="nw")
    tk.Button(w, text="单集下载", command=lambda: chioce_number(w, lb2, media_urls, texts, title)).place(x=345, y=5,
                                                                                                  anchor="nw")
    tk.Button(w, text="批量下载", command=lambda: chioce_number2(w, media_urls, texts, title)).place(x=405, y=5, anchor="nw")


def search(w, word_e):
    tk.Label(w, text="", width=200, height=30).place(x=5, y=75, anchor="nw")
    tk.Label(w, text="正在搜索...").place(x=5, y=85, anchor="nw")
    word = word_e.get()
    titles, type_urls = get_type_url(w, word)
    if len(type_urls):
        tk.Label(w, text="", width=200, height=30).place(x=5, y=75, anchor="nw")
        lb = tk.Listbox(w, bg="pink", width=34, height=18)
        lb.place(x=5, y=120, anchor="nw")
        tk.Label(w, text="找到以下资源 选择下载哪一部").place(x=5, y=90, anchor="nw")
        for i in range(len(type_urls)):
            item = "{0}  {1}".format(i + 1, titles[i])
            lb.insert(tk.END, item)
        tk.Button(w, text="确定", command=lambda: chioce_opton(w, lb, titles, type_urls)).place(x=220, y=80,
                                                                                           anchor="nw")  # 使用匿名函数传递参数
    else:
        tk.Label(w, text="", width=200, height=30).place(x=5, y=75, anchor="nw")
        tk.Label(w, text="没有找到任何记录").place(x=5, y=85, anchor="nw")
        print('没有找到任何记录')


