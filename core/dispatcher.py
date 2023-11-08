import os
from settings import DOMAINS, DomainKeys
from likiteka.page_scraping import scrape_pages as scrape_likiteka

from core.utilities import read_task, make_dir_in_data_dir, make_dir_in_log_dir, save_log
from core.exceptions import FailedDomainKey


from icecream import ic

SCRAPE_FUN_DICT = {
    DomainKeys.LIKITEKA.name: scrape_likiteka
}


def scrape_dispatcher(domain_key: str, task_file_path: str):
    if domain_key in SCRAPE_FUN_DICT:
        source_page_dir = make_dir_in_data_dir(domain_key.lower())
        drug_list = read_task(task_file_path)
        scrape_fun = SCRAPE_FUN_DICT[domain_key]

        refused_url = scrape_fun(domain_url=DOMAINS[domain_key], source_page_dir=source_page_dir, drug_list=drug_list)
        domain_log_dir = make_dir_in_log_dir(domain_key.lower())
        log_file_path = os.path.join(domain_log_dir, domain_key.lower() + "_scraped_refused_url.log")
        save_log(log_file_path, refused_url)
    else:
        raise FailedDomainKey(f'Not found key \'{domain_key}\' in {SCRAPE_FUN_DICT.keys()}')


if __name__ == "__main__":
    from settings import DEFAULT_TASK_FILE_PATH
    scrape_dispatcher(DomainKeys(0).name, DEFAULT_TASK_FILE_PATH)