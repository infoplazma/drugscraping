import os
from typing import List
import pandas as pd

import settings as stt
from core.utilities import read_excel, save_lines, read_log, dfs_to_excel, DFS_TYPE

from icecream import ic


def save_status(dfs: DFS_TYPE, target_dir: str):
    """
    Сохраняет итоговую статистику из целевого excel файла:

    Все уникальные значения форм выпуска в двух файлах
    первый файл 'task_release_forms.txt' - названия что были указаны в задании
    второй файл 'actual_release_forms.txt' - названия что фактически присутсвуют на сайте

    Все уникальные названия препаратов в двух файлах
    первый файл 'task_drugs.txt' - названия что были указаны в задании
    второй файл 'actual_product_names.txt' - названия что фактически присутсвуют на сайте
    """

    simply_release_forms = list()
    release_forms = list()
    drugs = list()
    product_names = list()
    for sheet_name, df in dfs.items():
        print(f"'{sheet_name}':{len(df)}")
        simply_release_forms.extend(df[stt.SIMPLY_RELEASE_FORM_COLUMN].unique().tolist())
        release_forms.extend(df[stt.RELEASE_FORM_COLUMN].unique().tolist())
        drugs.extend(df[stt.DRUG_COLUMN].unique().tolist())
        product_names.extend(df[stt.PRODUCT_NAME_COLUMN].unique().tolist())

    simply_release_forms_path = os.path.join(target_dir, 'task_release_forms.txt')
    release_forms_path = os.path.join(target_dir, 'actual_release_forms.txt')
    drugs_path = os.path.join(target_dir, 'task_drugs.txt')
    product_names_path = os.path.join(target_dir, 'actual_product_names.txt')

    os.makedirs(target_dir, exist_ok=True)

    save_lines(release_forms_path, sorted(set(release_forms)))
    print(f"task release forms saved: '{simply_release_forms_path}'")

    save_lines(simply_release_forms_path, sorted(set(simply_release_forms)))
    print(f"actual release forms saved: '{release_forms_path}'")

    save_lines(drugs_path, sorted(set(drugs)))
    print(f"task drugs saved: '{drugs_path}'")

    save_lines(product_names_path, sorted(set(product_names)))
    print(f"actual product names saved: '{product_names_path}'")


def filter_dfs_by_list(dfs: DFS_TYPE, task_list: List[str], column: str) -> DFS_TYPE:
    """
    Фильтрует dfs по совпадению значений колонки с именем: column со значениями присутствующими в листе: task_list
    """
    new_dfs: DFS_TYPE = dict()
    for sheet_name, df in dfs.items():
        new_df = df[df[column].isin(task_list)]
        if len(new_df) > 0:
            new_dfs[sheet_name] = new_df
            print(f"'{sheet_name}': {len(df)} ===> {len(new_df)}")

    return new_dfs


if __name__ == "__main__":
    likiteka_source_filepath = os.path.join(stt.EXCEL_DATA_DIR, 'likiteka.xlsx')
    dfs_ = read_excel(likiteka_source_filepath, disable_tqdm=False, desc_tqdm="Диагнозы")

    # likiteka_target_dir = os.path.join(stt.STATISTICS_DATA_DIR, stt.DomainKeys.LIKITEKA.name.lower())
    # save_statistics(dfs_, likiteka_target_dir)

    actual_release_forms = "temp/release_forms.txt"
    release_form_list_ = read_log(actual_release_forms)
    ic(release_form_list_)
    new_dfs_ = filter_dfs_by_list(dfs_, release_form_list_, stt.SIMPLY_RELEASE_FORM_COLUMN)

    likiteka_target_filepath = '../../tests/temp/likiteka_filtered.xlsx'
    dfs_to_excel(likiteka_target_filepath, new_dfs_, highlighted_columns=['release_form'])
    print(f"Отфильтрованный целевой файл сохранен: '{os.path.abspath(likiteka_target_filepath)}'")
