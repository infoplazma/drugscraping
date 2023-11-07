import os
from typing import Tuple, List, Dict

import pandas as pd
from colorama import Fore, Style

from settings import HTML_DATA_DIR, LOG_DIR
from settings import CUSTOM_DRUG_TAG, CUSTOM_PRODUCT_NAME_TAG, CUSTOM_URL_TAG


def add_tail(drug: str, product_name: str, url: str) -> str:
    return f"<{CUSTOM_DRUG_TAG}>{drug}</{CUSTOM_DRUG_TAG}>" + \
           f"<{CUSTOM_PRODUCT_NAME_TAG}>{product_name}</{CUSTOM_PRODUCT_NAME_TAG}>" + \
           f"<{CUSTOM_URL_TAG}>{url}</{CUSTOM_URL_TAG}>"


def save_refused_url(path: str, refused_url: Tuple[str, ...]) -> None:
    with open(path, 'w', encoding="utf-8") as fp:
        for data in refused_url:
            # write each data on a new line
            fp.write(",  ".join(data) + "\n")


def read_task(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as file:
        # reading the file
        data = file.read()
        data_list = [item.strip() for item in data.split('\n')]
        return [item.strip() for item in data_list if not item.startswith("#")]


def make_dir_in_data_dir(dir_name: str) -> str:
    dir_path = os.path.join(HTML_DATA_DIR, dir_name)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def make_dir_in_log_dir(dir_name: str) -> str:
    dir_path = os.path.join(LOG_DIR, dir_name)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def dfs_to_excel(path: str, dfs: Dict[str, pd.DataFrame], highlighted_columns: Tuple[str] = None, massage: str = None):
    if isinstance(dfs, pd.DataFrame):
        dfs: Dict[str, pd.DataFrame] = {"Sheet1": dfs}

    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        workbook = writer.book
        header_format = workbook.add_format({'bold': True, 'fg_color': '#FDE9D9', 'border': 1})
        special_header_format = workbook.add_format({'bold': True, 'fg_color': '#7CFC00', 'border': 1})
        text_wrap = workbook.add_format({'text_wrap': 'true'})
        for name, df in dfs.items():
            df.to_excel(writer, sheet_name=f"{name}", index=False, freeze_panes=(1, 0))
            # formatting sheet_name
            worksheet = writer.sheets[name]
            worksheet.set_column(0, len(df.columns) - 1, 40, text_wrap)
            for col_num, value in enumerate(df.columns.values):
                if highlighted_columns and value in highlighted_columns:
                    worksheet.write(0, col_num, value, special_header_format)
                else:
                    worksheet.write(0, col_num, value, header_format)

    if massage:
        print(massage)


def is_open_file(path: str) -> bool:
    if not os.path.isfile(path):
        return False
    try:
        with open(path, "r+", encoding='utf-8') as f:  # or "a+", whatever you need
            f.close()
            return False
    except IOError:
        print(Fore.RED + Style.BRIGHT + f"Please close file! '{path}'", end='')
        print(Style.RESET_ALL)
        return True
