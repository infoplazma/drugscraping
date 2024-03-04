"""
Добавление существующих препаратов к диагнозу
"""
import os
from typing import Any, Tuple, List, Dict
import json
import requests
from icecream import ic

import settings
from core.utilities import DFS_TYPE, read_excel, mkdir

DRUGS_ROUTER = r"v1/drugs"
SIMPLE_DRUG_ROUTER = r"v1/simple-drug"
REG_ROUTER = r"v1/regulations"
DRUGS_URL = r"v1/drugs-url"
USAGE_COLUMN_NAMES_URL = r"v1/usage-column"
USAGE_DOSAGE_URL = r"v1/usage-dosage"


def get_diagnoses(ip: str) -> List[Any]:
    r = requests.get(rf'http://{ip}/api/v1/diagnosis/list/', headers={'Accept': 'application/json'})
    if r.status_code == 200:
        return r.json()
    else:
        raise Exception(r.status_code)


def get_diagnosis_name(ip: str, diagnosis_id: int) -> str:
    diagnoses_map = {d['id']: d['name'] for d in get_diagnoses(ip)}
    return diagnoses_map[diagnosis_id]


def get_diagnosis_id(ip: str, name: str) -> int:
    diagnoses_map = {d['name']: d['id'] for d in get_diagnoses(ip)}
    return diagnoses_map[name]


def get_regulations(ip: str, diagnosis_id: int) -> List:
    r = requests.get(rf'http://{ip}/api/v1/diagnosis/{diagnosis_id}/', headers={'Accept': 'application/json'})
    if r.status_code == 200:
        res = r.json()
        regulations = res['regulations']
    else:
        raise Exception(r.status_code)

    return regulations


def is_drug_in_regulations_by_url(regulations: list, order: int, drug_url: str) -> bool:
    url_list = [reg['drug']['url'] for reg in regulations if reg['order'] == order]
    return drug_url in url_list


def is_drug_in_regulations_by_id(regulations: list, order: int, drug_id: str) -> bool:
    id_list = [reg['drug']['id'] for reg in regulations if reg['order'] == order]
    return drug_id in id_list


def get_all_drugs(ip: str) -> list:
    r = requests.get(rf'http://{ip}/api/{DRUGS_ROUTER}/', headers={'Accept': 'application/json'})
    if r.status_code == 200:
        drugs = r.json()
    else:
        raise Exception(r.status_code)
    return drugs


def get_drug_by_id(drug_id: int, all_drugs: list) -> tuple:
    return tuple(filter(lambda x: x['id'] == drug_id, all_drugs))


def get_drug_by_url(ip: str, url: str):
    r = requests.get(rf'http://{ip}/api/{DRUGS_URL}/', json={"url": f"{url}"}, headers={'Accept': 'application/json'})
    if r.status_code == 200:
        ids = r.json()
        if ids['ids']:
            drug_id = ids['ids'][0]
            r = requests.get(rf'http://{ip}/api/{DRUGS_ROUTER}{drug_id}/', headers={'Accept': 'application/json'})
            if r.status_code == 200:
                return r.json()
            else:
                return None
    else:
        raise Exception(r.status_code)


def get_drug_by_id(ip: str, drug_id: int) -> dict:
    r = requests.get(rf'http://{ip}/api/{DRUGS_ROUTER}/{drug_id}/', headers={'Accept': 'application/json'})
    if r.status_code == 200:
        drug = r.json()
    else:
        raise Exception(r.status_code)
    return drug


def update_usage_dosage(ip: str, drug_id: int, column_name: str, new_text: str) -> dict:
    if usage_dosage := get_usage_dosage_by_drug_id(ip, drug_id, column_name):
        del usage_dosage['column_name']
        usage_dosage_id = usage_dosage['id']
        # del usage_dosage['id']
        usage_dosage['text'] = new_text
        r = requests.put(rf'http://{ip}/api/{USAGE_DOSAGE_URL}/{usage_dosage_id}/', data=usage_dosage)
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception(r.status_code)


def get_usage_column_names(ip: str) -> List[Any]:
    r = requests.get(rf'http://{ip}/api/{USAGE_COLUMN_NAMES_URL}/', headers={'Accept': 'application/json'})
    if r.status_code == 200:
        usage_column_names = r.json()
    else:
        raise Exception(r.status_code)
    return usage_column_names


def get_usage_column_id(ip: str, column_name: str) -> int:
    usage_colum_map = {e['column_name']: e['id'] for e in get_usage_column_names(ip)}
    return usage_colum_map[column_name]


def get_usage_dosages(ip: str) -> List[Any]:
    r = requests.get(rf'http://{ip}/api/{USAGE_DOSAGE_URL}/', headers={'Accept': 'application/json'})
    if r.status_code == 200:
        usage_dosages = r.json()
    else:
        raise Exception(r.status_code)
    return usage_dosages


def get_usage_dosage_by_drug_id(ip: str, drug_id: int, column_name: str) -> dict:
    if drug := get_drug_by_id(ip, drug_id):
        if usage_dosage := tuple(filter(lambda x: x['column_name'] == column_name, drug['usagedosage'])):
            return usage_dosage[0]

    return {}


def append_regulation(ip: str, diagnosis_id: int, order: int, symptom: str, drug_id: int = None, drug_url: str = None,
                      regulations=None, is_disabled=True) -> Tuple[bool, Any]:
    """
    Добавление новой записи в диагноз если препарат существует в базе

    Возвращает два значения, True - при успешном добавлении, значение при успешном или код ошибки, None в случае сбоя.
    """
    if drug_id is None and drug_url is None:
        return False, "Должно быть указан только один из аргументов или drug_id или drug_url"
    elif drug_id and drug_url:
        return False, "Должно быть указан только один из аргументов или drug_id или drug_url"

    if regulations is None:
        regulations = get_regulations(ip, diagnosis_id)

    if drug_url is not None and is_drug_in_regulations_by_url(regulations, order, drug_url):
        return False, f"Препарат с таким {order=} и {drug_url=} уже привязан к диагнозу с {diagnosis_id=}"
    if drug_id is not None and is_drug_in_regulations_by_id(regulations, order, drug_id):
        return False, f"Препарат с таким {order=} и {drug_url=} уже привязан к диагнозу с {diagnosis_id=}"

    if drug_id is None:
        drug = get_drug_by_url(ip, drug_url)
        if drug:
            drug_id = int(drug['id'])
        else:
            return False, f"В базе не найден препарат с {drug_url=}"

    new_regulation = {"diagnosis": diagnosis_id,
                      "drug": drug_id,
                      "order": order,
                      "symptom": symptom,
                      "is_disabled": is_disabled}

    r = requests.post(rf'http://{ip}/api/{REG_ROUTER}/', data=new_regulation)
    if r.status_code == 201:
        return True, r.json()['drug']
    else:
        return False, r.status_code


def update_symptom(ip: str, diagnosis_id: int, drug_id: int, new_symptom: str, order: int = None):
    """
    Если order=None то для всех order
    """
    symptoms = []
    regulations = get_regulations(ip, diagnosis_id)
    if order is not None:
        regulations = [reg for reg in regulations if reg['drug']['id'] == drug_id and reg['order'] == order]
    else:
        regulations = [reg for reg in regulations if reg['drug']['id'] == drug_id]
    if not regulations:
        raise Exception(f"Не найдено ни одной записи для заданного условия {drug_id=}")
    for reg in regulations:
        old_symptom = reg['symptom']
        reg['symptom'] = new_symptom
        reg['drug'] = reg['drug']['id']
        reg_id = reg["id"]
        del reg["id"]

        r = requests.put(rf'http://{ip}/api/{REG_ROUTER}/{reg_id}/', data=reg)
        if r.status_code == 200:
            symptoms.append({"old_symptom": old_symptom, "reg": r.json()})
        else:
            symptoms.append({"Не удалось обновить симптом": old_symptom, "status_code": r.status_code})

    return symptoms


def append_regulation_from_excel(excel_path: str, ip: str, is_disabled=True):
    """
     diagnoses = dict[diagnosis_name: id]
    """
    dfs: DFS_TYPE = read_excel(excel_path)
    diagnoses_map = {d['name']: d['id'] for d in get_diagnoses(ip)}
    for diagnosis_name, df in dfs.items():
        if diagnosis_name not in diagnoses_map:
            print(
                f"'{diagnosis_name}' из excel файла не соответствует "
                f"названиям диагнозов в базе данных\n{list(diagnoses_map.keys())} !!!\n")
            continue

        diagnosis_id = diagnoses_map[diagnosis_name]
        print(f"\n{diagnosis_name=}  {diagnosis_id=}")
        print("=" * 120)
        df = df.drop_duplicates(subset=["url"], ignore_index=True)
        regulations = get_regulations(ip, diagnosis_id)
        for i in range(len(df)):
            print(append_regulation(
                ip, diagnosis_id, df.loc[i, "order"], df.loc[i, "symptom"], drug_url=df.loc[i, "url"],
                regulations=regulations, is_disabled=is_disabled))


def backup(ip: str, backup_dir: str):
    print("Backup через api базы данных:\nСкачивание займет определенное время...")

    mkdir(backup_dir)
    diagnosis_list_path = os.path.join(backup_dir, "diagnosis_list.json")

    headers = {'Accept': 'application/json'}

    print(f"\nloading diagnosis list...")
    diagnoses = get_diagnoses(ip)
    # r = requests.get(rf'http://{ip}/api/v1/diagnosis/list/', headers=headers)
    # Writing diagnosis file
    with open(diagnosis_list_path, "w", encoding="utf-8") as outfile:
        outfile.write(json.dumps(diagnoses))
        print(f"Все диагнозы из базы сохранены '{diagnosis_list_path}'")

    diagnosis_dict: Dict[int, str] = {diagnosis['id']: diagnosis['name'] for diagnosis in diagnoses}

    for pk, name in diagnosis_dict.items():
        print(f"\nloading {name}...")
        r = requests.get(rf'http://{ip}/api/v1/diagnosis/{pk}/', headers=headers)
        # Writing data to file
        path = os.path.join(backup_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as outfile:
            outfile.write(json.dumps(r.json()))
            print(f"Структура и препараты диагноза \"{name}\" сохранены: '{path}'")

    print()
    print("Процесс загрузки всех препаратов займет достаточное время...")
    all_drugs = get_all_drugs(ip)
    path = os.path.join(backup_dir, "all_drugs.json")
    with open(path, "w", encoding="utf-8") as outfile:
        outfile.write(json.dumps(all_drugs))
        print(f"Все препараты сохранены: '{path}'")

    usage_column_names = get_usage_column_names(ip)
    path = os.path.join(backup_dir, "usage_column_names.json")
    with open(path, "w", encoding="utf-8") as outfile:
        outfile.write(json.dumps(usage_column_names))
        print(f"Все usage column names сохранены: '{path}'")


if __name__ == "__main__":
    import re
    from dotenv import load_dotenv
    from pprint import pprint

    from apteka911.task_creator import TASK_DFS_PATH

    load_dotenv()

    IP = os.getenv("IP_SERVER")
    IP = os.getenv("IP_LOCAL")
    print(f"{IP=}")

    if IP is None:
        exit(7)
    ID = 41
    ID = 173

    ORDER = 2
    NEW_SYMPTOM = 'Температура тела от 38 и выше. У ребенка кожа бледная, "мраморная", сухая, конечности холодные. ' \
                  'Состояние ребенка нарушено-вялый, хочет спать, накрывается одеялом, ощущает озноб.'

    ORDER = 1
    NEW_SYMPTOM = 'Температура тела от 38,5 и выше. У ребенка кожа розовая, горячая ' \
                  'на ощупь, влажная . Конечности теплые.'

    DRUG_ID = 2500

    text_: str = get_usage_dosage_by_drug_id(IP, DRUG_ID, 'Спосіб застосування та дози')['text']
    text_ = text_.replace('_x000D_', "").replace(r'\t', "").replace(r'\r', "").replace(r'\n', "")
    text_ = re.sub(r'\s+', " ", text_)
    # pprint(text_)

    pprint(update_usage_dosage(IP, DRUG_ID, 'Спосіб застосування та дози', text_))

    # backup(IP, settings.BACKUP_DIR)

    # all_drugs_ = get_all_drugs(IP)
    # print(f"{len(all_drugs_)=}")
    # drug_ = get_drug_by_id(DRUG_ID, all_drugs_)
    # pprint(drug_)
    #
    # print("-"*120)
    # usage_dosages_ = get_usage_dosages(IP)
    # print(f"{len(usage_dosages_)=}")
    # pprint(get_usage_dosage_by_drug_id(DRUG_ID, usage_dosages_))
    # print(f"{get_usage_column_id(IP, 'Спосіб застосування та дози')=}")

    # try:
    #     pprint(update_symptom(IP, ID, new_symptom=NEW_SYMPTOM, drug_id=111111, order=ORDER))
    # except Exception as e:
    #     print(e)
    # append_regulation_from_excel(TASK_DFS_PATH, IP)
    # regs = get_regulations(ID)
    # pprint(regs)
    # is_drug_in_regulations(regs, None)

    # pprint(get_all_drugs(IP))

    # URL = "https://apteka911.ua/ua/shop/bofen-susp-oral-100mg-5ml-fl-100ml-p5030"
    #
    # pprint(get_drug_by_url(IP, URL))
