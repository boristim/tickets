import requests
from pathlib import Path
import hashlib
import re
import json
import logging
import http.client as http_client
import csv

http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

event_id = '3412160'

user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 YaBrowser/19.9.3.314 Yowser/2.5 Safari/537.36'
headers = {'User-Agent': user_agent,
           'Sec-Fetch-Mode': 'navigate',
           'Sec-Fetch-Site': 'none',
           'Sec-Fetch-User': '1',
           'Upgrade-Insecure-Requests': '1'
           }


def get_url(url, caching=1, req_method='get', post_data=None):
    file_name = 'tmp/' + hashlib.md5(url.encode('utf-8')).hexdigest() + '.html'
    file_path = Path(file_name)

    if not file_path.is_file() or caching != 1:
        if req_method == 'post':
            rr = requests.post(url, headers=headers, data=post_data)
        else:
            rr = requests.get(url, headers=headers)
        file = open(file_name, encoding='utf_8_sig', mode='w', errors='ignore')
        file.write(rr.text)
        file.close()

    file = open(file_name, encoding='utf_8_sig', mode='r')
    ret = file.read()
    file.close()
    return ret


html = get_url('https://www.viagogo.com/E-' + event_id)
add_id = re.findall('catid: (\d+)', html, re.IGNORECASE)

sections = []

if len(add_id) > 0:
    headers = {'User-Agent': user_agent,
               'X-Requested-With': 'XMLHttpRequest',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Site': 'same-origin'}
    url = 'https://www.viagogo.com/Browse/VenueMap/GetSvgData/' + event_id + '?categoryId=' + add_id[0]

    places = get_url(url, 1, 'post')
    answer = json.loads(places)
    for tier in answer['VenueMapConfiguration']:
        for sec in tier['secs']:
            if sec['q'] > 0:
                sections.append({'min': sec['min'], 'sec': sec['t'], 'tier': tier['n']})

csv_columns = ['tier', 'sec', 'min']
try:
    with open('result.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in sections:
            writer.writerow(data)
except IOError:
    print("I/O error")
