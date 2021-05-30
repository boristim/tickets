import requests
import re
import json
import csv
import yaml

with open("config.yaml", "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exception:
        print(exception)
        exit(1)
    finally:
        stream.close()

headers = {'User-Agent': config['user_agent'], 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '1', 'Upgrade-Insecure-Requests': '1'}
req = requests.get(config['url']['html'] % config['event_id'], headers=headers)
add_id = re.findall("catid: (\d+)", req.text, re.IGNORECASE)
sections = []
if len(add_id) > 0:
    headers = {'User-Agent': config['user_agent'], 'X-Requested-With': 'XMLHttpRequest', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin'}
    req = requests.post(config['url']['ajax'] % (config['event_id'], add_id[0]), headers=headers)
    answer = json.loads(req.text)
    for tier in answer['VenueMapConfiguration']:
        for sec in tier['secs']:
            if sec['q'] > 0:
                sections.append({'min': sec['min'], 'sec': sec['t'], 'tier': tier['n']})

csv_columns = ['tier', 'sec', 'min']
try:
    with open(config['result_file'], 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in sections:
            writer.writerow(data)
except IOError as exception:
    print(exception)
    exit(2)
