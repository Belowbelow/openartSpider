import pickle

path = "data.pickle"
with open(path, 'rb') as f:
    data = pickle.load(f)
    for i in data:
        print(i)

def download_pic(url):