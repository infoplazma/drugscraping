import os
from typing import Tuple

from colorama import Fore, Style

import settings as stt
from core.maker_lib.inspection import inspect
from core.maker_lib.release_forms_found import reload_release_form_files

from core.maker_lib.task_file_validation import validate_task_file
from core.similarity import read_substitution_list, save_unrecognizable
from settings import DOMAINS, DomainKeys, TASK_FILE_PATH, TEMP_DATA_DIR, EXCEL_DATA_DIR
from likiteka.page_scraping import scrape_pages as scrape_likiteka

from core.utilities import read_log, make_dir_in_data_dir, make_dir_in_log_dir, save_log
from core.exceptions import FailedDomainKey
from core.maker_lib.page_parsing_maker import make_temp_parsed_file
from core.maker_lib.target_excel_file_maker import make_target_excel_file


SCRAPE_FUN_DICT = {
    DomainKeys.LIKITEKA.name: scrape_likiteka
}


def make_scraping(domain_key: str):
    if domain_key.upper() in SCRAPE_FUN_DICT:

        validate_task_file()
        domain_key = domain_key.upper()

        source_page_dir = make_dir_in_data_dir(domain_key.lower())
        drug_list = read_log(TASK_FILE_PATH)
        scrape_fun = SCRAPE_FUN_DICT[domain_key]

        refused_url = scrape_fun(domain_url=DOMAINS[domain_key], source_page_dir=source_page_dir, drug_list=drug_list)
        domain_log_dir = make_dir_in_log_dir(domain_key.lower())
        log_file_path = os.path.join(domain_log_dir, domain_key.lower() + "_scraped_refused_url.log")
        save_log(log_file_path, refused_url)
    else:
        raise FailedDomainKey(f'Not found key \'{domain_key}\' in {SCRAPE_FUN_DICT.keys()}')


def make_parsing(domain_key: str):
    if domain_key.upper() in SCRAPE_FUN_DICT:

        validate_task_file()
        domain_key = domain_key.lower()

        temp_file_path = os.path.join(TEMP_DATA_DIR, domain_key + "_parsed.csv")
        # Путь где будет сохранен файл
        target_excel_file_path = os.path.join(EXCEL_DATA_DIR, domain_key + ".xlsx")

        df_parsed = make_temp_parsed_file(domain_key, TASK_FILE_PATH, temp_file_path)
        maker = make_target_excel_file(temp_file_path, target_excel_file_path)
        reload_release_form_files(maker, df_parsed)
    else:
        raise FailedDomainKey(f'Not found key \'{domain_key}\' in {SCRAPE_FUN_DICT.keys()}')


def make_inspecting(domain: str) -> Tuple[str]:
    source_dir = os.path.join(stt.HTML_DATA_DIR, domain.lower())
    if not os.path.isdir(source_dir):
        print(Fore.RED + Style.BRIGHT + f"Не найдена папка '{source_dir}'", end='')
        print(Fore.YELLOW + Style.BRIGHT + "\n...terminated")
        print(Style.RESET_ALL)
        exit()

    return inspect(source_dir)


def make_unrecognizable(release_form: str = None) -> Tuple[str]:
    if os.path.isfile(stt.UNRECOGNIZABLE_FILE_PATH):
        if release_form:
            save_unrecognizable(stt.UNRECOGNIZABLE_FILE_PATH, [release_form])
        return read_substitution_list(stt.UNRECOGNIZABLE_FILE_PATH)
    else:
        print(Fore.RED + Style.BRIGHT + f"Не найден файл:'{stt.UNRECOGNIZABLE_FILE_PATH}'", end='')
        print(Fore.YELLOW + Style.BRIGHT + "\n...terminated")
        print(Style.RESET_ALL)
        exit()




