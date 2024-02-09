import requests
from icecream import ic

from settings import API_URL


# IP_LOCAL = "127.0.0.1:8000"
# IP_SERVER = "185.174.220.122"
# IP = IP_SERVER


r = requests.get(rf'{API_URL}drugs-url/', json={"url": "https://apteka911.ua/ua/shop/bofen-susp-oral-100mg-5ml-fl-100ml-p5030"}, headers={'Accept': 'application/json'})
if r.status_code == 200:
    ids = r.json()
    ic(ids['ids'])
    if ids['ids']:
        drug_id = ids['ids'][0]
        ic(drug_id)
        r = requests.get(rf'{API_URL}/drugs/{drug_id}/', headers={'Accept': 'application/json'})
        if r.status_code == 200:
            data = r.json()
            ic(data)
else:
    print(r.status_code)
