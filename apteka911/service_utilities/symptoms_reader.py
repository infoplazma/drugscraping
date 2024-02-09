"""
Формирует списки симптомов по диагнозам
"""
from typing import Dict
import pandas as pd
from core.utilities import read_excel_package, is_open_file


def read_symptoms(dir_path: str) -> Dict[str, pd.DataFrame]:
    new_dfs: Dict[str, pd.DataFrame] = dict()
    dfs = read_excel_package(dir_path)
    for diagnosis, df in dfs.items():
        new_df = df[["order", "symptom"]]
        new_df = new_df.drop_duplicates(subset=['symptom'])
        new_df.insert(1, "sub_order", [0] * len(new_df), True)
        # new_df.loc[:, "sub_order"] = [0] * len(new_df)
        new_dfs[diagnosis] = new_df

    return new_dfs


if __name__ == "__main__":
    import os
    import settings
    from core.utilities import dfs_to_excel

    dfs_ = read_symptoms(settings.TASK_DIR)
    for diagnosis_, df_ in dfs_.items():
        print(f"\n{diagnosis_}")
        print("-"*120)
        print(*df_.to_records(index=False), sep="\n")

    SYMPTOMS_PATH = os.path.join(settings.APTEKA911, 'data', 'symptoms.xlsx')
    if not is_open_file(SYMPTOMS_PATH):
        dfs_to_excel(SYMPTOMS_PATH, dfs_, highlighted_columns=["symptom"], massage=f"saved at: '{SYMPTOMS_PATH}'")

