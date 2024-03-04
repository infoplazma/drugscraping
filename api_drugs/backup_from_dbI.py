"""
Backup через api базы данных
"""
import os
import requests
import json

from typing import Dict

from pprint import PrettyPrinter
from core.utilities import mkdir
from api_drugs.api_utilities import get_diagnoses


def backup(ip: str, diagnoses_dir: str):
    print("Backup через api базы данных:\nСкачивание займет определенное время...")
    mkdir(diagnoses_dir)
    diagnosis_list_path = os.path.join(diagnoses_dir, "diagnosis_list.json")

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
        path = os.path.join(diagnoses_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as outfile:
            outfile.write(json.dumps(r.json()))
            print(f"Структура и препараты диагноза \"{name}\" сохранены: '{path}'")
