import os
from typing import Tuple, List

from settings import HTML_DATA_DIR, LOG_DIR
from settings import CUSTOM_DRUG_TAG, CUSTOM_PRODUCT_NAME_TAG, CUSTOM_URL_TAG


def add_tail(drug: str, product_name: str, url: str) -> str:
    return f"<{CUSTOM_DRUG_TAG}>{drug}</{CUSTOM_DRUG_TAG}>" + \
           f"<{CUSTOM_PRODUCT_NAME_TAG}>{product_name}</{CUSTOM_PRODUCT_NAME_TAG}>" + \
           f"<{CUSTOM_URL_TAG}>{url}</{CUSTOM_URL_TAG}>"


def save_refused_url(path: str, refused_url: Tuple[str, str]) -> None:
    with open(path, 'w', encoding="utf-8") as fp:
        for (drug, url) in refused_url:
            # write each url on a new line
            fp.write(f"{drug}, {url}\n")


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
