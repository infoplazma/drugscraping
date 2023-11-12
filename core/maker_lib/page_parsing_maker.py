import os

from colorama import Fore, Style

import settings as stt
from core.utilities import is_open_file, make_dir_in_data_dir, dfs_to_excel, make_dir_in_log_dir, save_log, read_log
from core.utilities import reset_column_positions
from settings import HTML_DATA_DIR, EXCEL_DATA_DIR, COLUMN_NAMES
from likiteka.page_parsing import parse_pages

# from icecream import ic
# stt.DEBUG = False


def make_temp_parsed_file(domain: str, task_file_path: str, temp_file_path: str):

    if os.path.isfile(temp_file_path):
        print(f"Загрузка распарсенных данных произойдет из временного файла.")
        print(f"Если нужно распарсить заново, то удалите временный файл '{temp_file_path}'")
        _ = input("Press any key:")
        return

    source_dir = os.path.join(HTML_DATA_DIR, domain)
    if not os.path.isdir(source_dir):
        print(Fore.RED + Style.BRIGHT + f"Не найдена папка '{source_dir}'", end='')
        print(Style.RESET_ALL)
        exit()

    if stt.DEBUG:
        excel_parsed_path = os.path.join(EXCEL_DATA_DIR, domain + "_parsed.xlsx")
        make_dir_in_data_dir(EXCEL_DATA_DIR)
        if is_open_file(excel_parsed_path):
            exit()

    make_dir_in_log_dir(stt.TEMP_DATA_DIR)
    if is_open_file(temp_file_path):
        exit()

    drug_list = read_log(task_file_path)

    df, refused_url = parse_pages(source_page_dir=source_dir, drug_list=drug_list)
    if len(df) == 0:
        print(Fore.RED + Style.BRIGHT + "Не удалось распарсить ни один препарат.", end='')
        print(Style.RESET_ALL)
        exit()

    df = reset_column_positions(df, COLUMN_NAMES)

    # Сохраняем временный файл с распарсенными данными
    df.to_csv(temp_file_path, index=False)
    if stt.DEBUG:
        dfs_to_excel(excel_parsed_path, {domain: df}, highlighted_columns=['Спосіб застосування та дози'])

    domain_log_dir = make_dir_in_log_dir(domain)
    log_file_path = os.path.join(domain_log_dir, domain + "_parsed_refused_url.log")
    save_log(log_file_path, refused_url)


if __name__ == "__main__":
    from settings import DomainKeys

    domain = DomainKeys.LIKITEKA.name.lower()
    temp_file_path = os.path.join(stt.TEMP_DATA_DIR, domain + "_parsed.csv")

    make_temp_parsed_file(domain, stt.TASK_FILE_PATH, temp_file_path)
