import requests
import json
from datetime import datetime, timedelta

url = "http://ergast.com/api/f1/2020/1.json"
payload={}
headers = {}
response = requests.get(url, headers=headers, data=payload)
j = response.json()
race = j['MRData']['RaceTable']['Races'][0]
season = race['season']
round = race['round']
dts = race['date']+' '+race['time']
dt = datetime.strptime(race['date']+race['time'], "%Y-%m-%d%H:%M:%SZ") + timedelta(hours = 8)
print(dt)
purl = race['Circuit']['url'].rsplit('/', 1)[-1]
print(purl)
url = "http://en.wikipedia.org/w/api.php?action=query&titles="+purl+"&prop=pageimages&format=json&pithumbsize=200"
payload={}
headers = {}
response = requests.get(url, headers=headers, data=payload)
j = response.json()
imgUrl = j['query']['pages']
print(imgUrl)
for i in imgUrl:
	imgUrl = imgUrl[i]
print(imgUrl['thumbnail']['source'])
