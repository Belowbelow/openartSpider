import pickle
import requests
import threading
import queue

path = "data.pickle"
headers = { 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:65.0) Gecko/20100101 Firefox/65.0' }

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
    except requests.exceptions.ReadTimeout as e:
        print(f'{filename} download failed')

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

# 获取图片信息
with open(path, 'rb') as f:
    data = pickle.load(f)
    # 将图片路径与链接放到工作队列中
    work_queue = queue.Queue()
    pic_num = 0
    for i in data:
        pic_index = 0
        for url in i['image_urls']:
            work_queue.put([url, f'./pic2/pic_{pic_num}_{pic_index}.webp'])
            pic_index += 1
        pic_num += 1

    # 多线程爬图片
    threads = []
    for i in range(1, 9):
        thread = get_pic_thread(str(i), work_queue)
        threads.append(thread)
        thread.start()

    # 等待线程结束
    for t in threads:
        t.join()

