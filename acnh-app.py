import urllib, requests
import flask, os, json
from apikey import api_key

# time, date, and location request
url = 'https://timezoneapi.io/api/ip/?token=' + api_key
response = requests.get(url)
data = response.json()
time = data['data']['datetime']['time']

def timesplit(time_str):
    time = time_str.split(':')
    times = {
        'hour': time[0],
        'minute': time[1],
        'second': time[2]
    }
    return times
print(timesplit(time)['hour'])

villager = urllib.request.urlopen('http://acnhapi.com/v1/villagers/1')
vill = json.load(villager)

# 