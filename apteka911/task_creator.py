"""
После парсинга создает DataFrame для загрузки на сайт
"""
import os
from typing import Tuple, List, Dict
import pandas as pd

import settings
from core.utilities import DFS_TYPE, read_excel, dfs_to_excel


TASK_DFS_PATH = os.path.join(settings.APTEKA911, "data", "drugs.xlsx")


def create_task_dfs(task_df: pd.DataFrame, parsed_drugs_df: pd.DataFrame, symptoms_dfs: DFS_TYPE) -> DFS_TYPE:
    dfs: Dict[str, List[dict]] = dict()
    not_found_drugs: List[str] = list()
    # "diagnosis", "symptom", "sub_symptom", "drug", "release_form"
    for ind in task_df.index:

        diagnosis = task_df['diagnosis'][ind]
        drug = task_df['drug'][ind]
        order = int(task_df['symptom'][ind])
        simply_release_form = task_df['release_form'][ind]

        drugs = find_drugs(drug, parsed_drugs_df.drop_duplicates())
        if not drugs['drug']:
            print(f"Not found drug:'{drug}' in diagnosis:'{diagnosis}'")
            not_found_drugs.append(drug)
            continue

        symptom_list = find_symptoms(order, diagnosis, symptoms_dfs)
        if not symptom_list:
            print(f"Not found symptoms for drug:'{drug}' in diagnosis:'{diagnosis}'")
            symptom = ""
        else:
            symptom = symptom_list[0]

        # Заполнение записи
        if diagnosis not in dfs:
            dfs[diagnosis] = list()

        for i in range(len(drugs['drug'])):
            dfs[diagnosis].append(
                {'order': order,
                 "drug": drug,
                 'symptom': symptom,
                 'product_name': drugs['product_name'][i],
                 'trade_name': drugs['Торгівельна назва'][i],
                 'active_ingredients': drugs['Діючі речовини'][i],
                 'simply_release_form': simply_release_form,
                 'release_form': drugs['Форма випуску'][i],
                 'composition': drugs['Кількість в упаковці'][i],
                 'children': "",
                 'Спосіб застосування та дози': drugs['text'][i],
                 'url': drugs['url'][i],
                 }
            )

    dfs = {diagnosis: pd.DataFrame(data_list) for diagnosis, data_list in dfs.items()}
    return dfs, not_found_drugs


def find_drugs(drug: str, df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Поиск препарата по названию в таблице из apteka911/service_utilities/one_drive_txt_file_to_df.py
    """
    return df[df['drug'] == drug].to_dict(orient='list')


def find_symptoms(order: int, diagnosis: str, symptoms_dfs: DFS_TYPE) -> List[str]:
    """
    Поиск симптома по номеру order и по диагнозу в таблице из
    файла по пути apteka911.service_utilities.symptoms_creator.SYMPTOMS_PATH
    """
    df = symptoms_dfs[diagnosis]
    return df[df['order'] == order]['symptom'].values.tolist()


if __name__ == "__main__":
    from icecream import ic

    from core.utilities import is_open_file
    from apteka911.service_utilities.one_drive_txt_file_to_df import transform_to_df
    from apteka911.service_utilities.symptoms_creator import SYMPTOMS_PATH
    from apteka911.page_parsing import PARSED_DATA_PATH

    symptoms_dfs_ = read_excel(SYMPTOMS_PATH)
    # symptom_list_ = find_symptoms(6, "Корь", symptoms_dfs_)
    # ic(symptom_list_)

    parsed_drugs_df_ = pd.read_csv(PARSED_DATA_PATH)
    task_df_ = transform_to_df(settings.ONE_DRIVE_DIR)

    dfs_, not_found_drugs_ = create_task_dfs(task_df_, parsed_drugs_df_, symptoms_dfs_)
    ic(dfs_)

    if not is_open_file(TASK_DFS_PATH):
        dfs_to_excel(TASK_DFS_PATH, dfs_, highlighted_columns=["drug", "product_name", "Спосіб застосування та дози"], massage=f"dfs saved: '{TASK_DFS_PATH}'")

