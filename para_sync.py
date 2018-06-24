import requests

urls = ['http://pic1.win4000.com/wallpaper/7/53bb814e13a63.jpg',
        'http://pic1.win4000.com/wallpaper/0/540ec117e8f01.jpg',
        'http://pic1.win4000.com/wallpaper/0/540ec110ba06b.jpg']

for url in urls:
    resp = requests.get(url)
    with open('{}'.format(url.split('/')[-1]), 'wb') as f:
        f.write(resp.content)
