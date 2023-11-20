import os
import re

import pandas as pd

from colorama import Fore, Style

import settings as stt
from core.utilities import is_open_file, make_dir_in_data_dir, dfs_to_excel, make_dir_in_log_dir, save_log, read_log
from core.utilities import reset_column_positions
from settings import HTML_DATA_DIR, EXCEL_DATA_DIR, COLUMN_NAMES
from likiteka.page_parsing import parse_pages
from core.maker_lib.task_file_validation import validate_task_list, validate_task_file


# from icecream import ic
# stt.DEBUG = False


def make_temp_parsed_file(domain: str, task_file_path: str, temp_file_path: str) -> pd.DataFrame:
    """
    Осуществляет валидацию и после возвращает распарсенную таблицу в формате pd.DataFrame
    :param domain:
    :param task_file_path: файл с перечнем лекарств которые нужно распарсить
    :param temp_file_path:

    :return: возвращает распарсенную таблицу в формате pd.DataFrame

    """
    validate_task_file()

    if os.path.isfile(temp_file_path):
        print(f"Загрузка распарсенных данных произойдет из раннее созданого временного файла.")
        print(f"Если нужно распарсить заново, то завершите процесс и удалите\nвременный файл: '{temp_file_path}'")
        try:
            key = input("\nНаберите exit либо Ctr+C для завершения процесса или Enter для продолжения:")
        except KeyboardInterrupt:
            print(Fore.YELLOW + Style.BRIGHT + "\n\n...terminated")
            print(Style.RESET_ALL)
            exit(7)
        else:
            if re.search("exit", key, flags=re.I):
                print(Fore.YELLOW + Style.BRIGHT + "\n...terminated")
                print(Style.RESET_ALL)
                exit(7)

    source_dir = os.path.join(HTML_DATA_DIR, domain)
    if not os.path.isdir(source_dir):
        print(Fore.RED + Style.BRIGHT + f"Не найдена папка '{source_dir}'", end='')
        print(Fore.YELLOW + Style.BRIGHT + "\n...terminated")
        print(Style.RESET_ALL)
        exit()

    if stt.DEBUG:
        excel_parsed_path = os.path.join(EXCEL_DATA_DIR, domain + "_parsed.xlsx")
        make_dir_in_data_dir(EXCEL_DATA_DIR)
        if is_open_file(excel_parsed_path):
            exit()

    make_dir_in_log_dir(stt.TEMP_DATA_DIR)
    if is_open_file(temp_file_path):
        print(Fore.YELLOW + Style.BRIGHT + "\n...terminated")
        exit()

    drug_list = read_log(task_file_path)

    df, refused_url = parse_pages(source_page_dir=source_dir, drug_list=drug_list)
    if len(df) == 0:
        print(Fore.RED + Style.BRIGHT + "Не удалось распарсить ни один препарат.", end='')
        print(Fore.YELLOW + Style.BRIGHT + "\n...terminated")
        print(Style.RESET_ALL)
        exit()

    df = reset_column_positions(df, COLUMN_NAMES)
    # remove nan values
    df.dropna(subset=[stt.DRUG_COLUMN, stt.RELEASE_FORM_COLUMN], inplace=True)
    # clear whitespace '\xa0'
    _clear = lambda x: re.sub(r"\s+", " ", str(x)).strip() if isinstance(x, str) else x
    df = df.apply(_clear)

    # Сохраняем временный файл с распарсенными данными
    df.to_csv(temp_file_path, index=False)
    print(f"Временный файл сохранен:'{temp_file_path}'")

    if stt.DEBUG:
        dfs_to_excel(excel_parsed_path, {domain: df}, highlighted_columns=['Спосіб застосування та дози'])

    domain_log_dir = make_dir_in_log_dir(domain)
    log_file_path = os.path.join(domain_log_dir, domain + "_parsed_refused_url.log")
    save_log(log_file_path, refused_url)

    return df


if __name__ == "__main__":
    from settings import DomainKeys

    domain = DomainKeys.LIKITEKA.name.lower()
    temp_file_path = os.path.join(stt.TEMP_DATA_DIR, domain + "_parsed.csv")

    make_temp_parsed_file(domain, stt.TASK_FILE_PATH, temp_file_path)
