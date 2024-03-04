import requests
from icecream import ic


def get_drug_by_url(api_url: str, url: str):
    r = requests.get(rf'{api_url}drugs-url/', json={"url": f"{url}"}, headers={'Accept': 'application/json'})
    if r.status_code == 200:
        ids = r.json()
        ic(ids['ids'])
        if ids['ids']:
            drug_id = ids['ids'][0]
            ic(drug_id)
            r = requests.get(rf'{api_url}/drugs/{drug_id}/', headers={'Accept': 'application/json'})
            if r.status_code == 200:
                data = r.json()
                ic(data)
    else:
        print(r.status_code)


if __name__ == "__main__":
    from settings import API_URL
    get_drug_by_url(API_URL, "https://apteka911.ua/ua/shop/bofen-susp-oral-100mg-5ml-fl-100ml-p5030")

