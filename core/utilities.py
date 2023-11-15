import os
import re
from typing import Tuple, List, Dict, TypeAlias

import pandas as pd
from colorama import Fore, Style
from tqdm import tqdm

from settings import HTML_DATA_DIR, LOG_DIR
from settings import CUSTOM_DRUG_TAG, CUSTOM_PRODUCT_NAME_TAG, CUSTOM_URL_TAG
from settings import URL_COLUMN

LOG_SEP = ' | '
STANDARD_SHEET: str = r"\w"
DFS_TYPE: TypeAlias = Dict[str, pd.DataFrame]


def add_tail(drug: str, product_name: str, url: str) -> str:
    return f"<{CUSTOM_DRUG_TAG}>{drug}</{CUSTOM_DRUG_TAG}>" + \
           f"<{CUSTOM_PRODUCT_NAME_TAG}>{product_name}</{CUSTOM_PRODUCT_NAME_TAG}>" + \
           f"<{CUSTOM_URL_TAG}>{url}</{CUSTOM_URL_TAG}>"


def save_log(path: str, log_list: List[Tuple[str, ...]]) -> None:
    with open(path, 'w', encoding="utf-8") as fp:
        for data in log_list:
            # write each data on a new line
            fp.write(LOG_SEP.join(map(str, data)) + "\n")


def save_lines(path: str, lines: List[str]) -> None:
    with open(path, 'w', encoding="utf-8") as fp:
        for line in lines:
            # write each data on a new line
            fp.write(str(line) + "\n")


def read_log(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as file:
        # reading the file
        data = file.read()
        data_list = [item.strip() for item in data.split('\n')]
        return [item.strip() for item in data_list if item and not item.startswith("#")]


def parse_log_lines(lines: List[str]) -> List[List[str]]:
    return [line.split(LOG_SEP) for line in lines]


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


def read_excel(file_path: str, disable_tqdm=True, desc_tqdm='files') -> DFS_TYPE:
    dfs: Dict[str, pd.DataFrame] = dict()
    file = os.path.basename(file_path)
    if not str(file).startswith("~$") and (str(file).endswith(".xls") or str(file).endswith(".xlsx")):
        xl = pd.ExcelFile(file_path)
        for sheet_name in tqdm(xl.sheet_names, desc=desc_tqdm, ncols=100, disable=disable_tqdm):
            if re.match(STANDARD_SHEET, sheet_name):
                dfs[sheet_name] = pd.read_excel(file_path, sheet_name=sheet_name)
    return dfs


def read_excel_package(dir_path: str, disable_tqdm=True, desc_tqdm='files') -> DFS_TYPE:
    dfs: Dict[str, pd.DataFrame] = dict()
    path_list = get_excel_path_list(dir_path)
    for path in path_list:
        new_dfs = read_excel(path, disable_tqdm, desc_tqdm)
        if intersection := set(dfs.keys()).intersection(set(new_dfs.keys())):
            raise ValueError(f"Пересечения названий Excel листов: {intersection=}")
        dfs.update(new_dfs)
    return dfs


def get_excel_path_list(dir_path: str) -> List[str]:
    file_list: List[str] = list()
    for root, _, dir_files in os.walk(dir_path):
        for file in dir_files:
            if not str(file).startswith("~$") and (str(file).endswith(".xls") or str(file).endswith(".xlsx")):
                path = os.path.abspath(os.path.join(root, file))
                file_list.append(path)

    return file_list


def reset_column_positions(df: pd.DataFrame, position_pattern: List[str]) -> pd.DataFrame:
    """
    Устанавливает порядок следования колонок по образцу position_pattern
    Последние две колонки из position_pattern устанавливает последними в df.
    """
    new_columns = [col for col in df.columns.tolist() if col in position_pattern]
    new_columns.remove(URL_COLUMN)
    new_columns.append(URL_COLUMN)
    return df[new_columns]


def check_column_names_in_df(df: pd.DataFrame, required_column_names: List[str]):
    if not set(required_column_names).issubset(set(df.columns.tolist())):
        raise ValueError(f"Not found required columns {set(required_column_names).difference(set(df.columns.tolist()))}")
