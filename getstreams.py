url = 'https://mcloudpush.cmc.zju.edu.cn:10443/streams'

import requests

import json

response = requests.get(url)
data = response.json()

streamid = []

for i in data["streams"]:
    streamid.extend(i.keys())

print(streamid)