from urllib.request import urlopen
from bs4 import BeautifulSoup as bf
import json
import pickle
import time

"""
根据关键词，获取openart上对应的图片（数量可调节，这里设置为90张左右）
包括：
图片本身
图片的尺寸
图片生成所用的模型
图片生成的关键词(prompt)
"""

# 在这里设置关键词
key_words = ["man", "woman"]

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
    html = urlopen(url).read()
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
            data['image_urls'] = i['image_url']
        ret.append(data)
    return ret

# 整合上方两个函数，根据关键词，直接获取对应大约90张图片的链接
def get_pic_link(key_words):
    print("crawling begin")
    urls = get_url_from_key_words(key_words)
    ret = []
    for url in urls:
        print(f'crawling {url}')
        ret += get_key_link(url)
        time.sleep(0.5)
    print("crawling end")
    return ret

# 将获取到的数据保存下来
s = get_pic_link(key_words)
with open("data.pickle", 'wb') as f:
    pickle.dump(s, f)