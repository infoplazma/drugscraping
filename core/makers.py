import os
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
    if domain_key in SCRAPE_FUN_DICT:
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
    if domain_key in SCRAPE_FUN_DICT:
        domain_key = domain_key.lower()
        temp_file_path = os.path.join(TEMP_DATA_DIR, domain_key + "_parsed.csv")
        # Путь где будет сохранен файл
        target_excel_file_path = os.path.join(EXCEL_DATA_DIR, domain_key + ".xlsx")

        make_temp_parsed_file(domain_key, TASK_FILE_PATH, temp_file_path)
        make_target_excel_file(temp_file_path, target_excel_file_path)
    else:
        raise FailedDomainKey(f'Not found key \'{domain_key}\' in {SCRAPE_FUN_DICT.keys()}')


if __name__ == "__main__":
    # make_scraping(DomainKeys(0).name)
    make_parsing(DomainKeys(0).name)
