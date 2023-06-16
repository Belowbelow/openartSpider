import json
import requests
import threading
import queue
import os
import time


"""
根据关键词, 获取openart上对应的图片(数量可调节, 这里设置为90张左右)
包括：
1. 图片本身
2. 图片的尺寸
3. 图片生成所用的模型
4. 图片生成的关键词(prompt)
"""

# 设置请求头，模拟用户访问
headers = { 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:65.0) Gecko/20100101 Firefox/65.0' }

# 根据关键词获得所对应的链接
def get_url_from_key_words(key_words):
    # 链接头 因为openart是动态网页，这里通过浏览器中的网络选项里的XHR找到json数据包
    url_head = "https://openart.ai/api/search?source=any&type=both&query="
    # 链接尾部，每30张图片一组
    url_tail = "&cursor="
    url_key = key_words[0]
    for kw in key_words[1:]:
        url_key += '%20' + kw
    
    # 组合url
    url1 = url_head + url_key + url_tail
    # 获取第二组图片的链接
    url2 = url1 + '30'
    # 获取第三组图片的链接
    url3 = url1 + '60'
    # 将链接返回
    return [url1, url2, url3]

# 根据链接获取每一张图片所对应的具体网页信息
def get_key_link(url):
    # 创建请求
    response = requests.get(url, headers=headers)
    html = response.content
    json_data = json.loads(html)
    ret = []
    for i in json_data['items']:
        data = dict()
        data['ai_model'] = i['ai_model']
        data['prompt'] = i['prompt']
        data['img_height'] = i['image_height']
        data['image_width'] = i['image_width']
        # 有些图片对应的链接只有一个，需要分支处理
        if 'image_urls' in i:
            data['image_urls'] = i['image_urls']
        else:
            data['image_urls'] = [i['image_url']]
        ret.append(data)
    return ret

# 整合上方两个函数，根据关键词，直接获取对应大约90张图片的信息
def get_pic_link(key_words):
    print("crawling begin")
    urls = get_url_from_key_words(key_words)
    ret = []
    for url in urls:
        print(f'crawling {url}')
        ret += get_key_link(url)
    print("crawling end")
    return ret

# 下面是获取图片的爬虫

# 根据链接和路径保存图片
def get_pic(url, filename):
    html = requests.get(url, headers=headers, timeout=2)
    with open(filename, 'wb') as f:
        f.write(html.content)
    print(f'{filename} download success')

# 根据队列下载图片
def get_pic_t(q):
    data = q.get()
    url = data[0]
    filename = data[1]
    try:
        get_pic(url, filename)
        # 设置一下缓冲时间，防止被屏蔽
        time.sleep(0.1)

    # 这里只有爬取失败才会出现该错误
    except requests.exceptions.ReadTimeout as e:
        print(f'{filename} download failed, retry')
        # 将超时的链接放回队列，重新爬取
        q.put([url, filename])

# 下载图片的线程
class get_pic_thread(threading.Thread):
    def __init__(self, name, q):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q

    def run(self):
        print(f'Start thread {self.name}')
        while True:
            if not self.q.empty():
                get_pic_t(self.q)
            else:
                break
        print(f'Exiting thread {self.name}')

# 在这里设置关键词
key_words = ["girl", "woman", "young", "beautiful"]

# 在这里设置图片保存路径
path = './pic5'
if not os.path.exists(path):
    os.makedirs(path)

# 根据关键词获取对应的90张左右的图片信息
data = get_pic_link(key_words)

# 将图片路径与链接放到工作队列中
work_queue = queue.Queue()
pic_num = 0
for i in data:
    pic_index = 0
    for url in i['image_urls']:
        work_queue.put([url, f'{path}/pic_{pic_num}_{pic_index}.webp'])
        pic_index += 1
    pic_num += 1

# 创建线程池
threads = []

try:
    # 这里设置线程数量为8
    for i in range(1, 9):
        thread = get_pic_thread(str(i), work_queue)
        threads.append(thread)
        thread.start()

    # 等待线程结束
    for t in threads:
        t.join()
except requests.exceptions.ConnectionError as e:
    print(f'链接失败，重新尝试')
except ConnectionResetError as e:
    print(f'链接失败，重新尝试')