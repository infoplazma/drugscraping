"""
проверяем какие перепараты соскрепленны для конкретного домена
"""
import codecs
import os
from typing import Tuple, Set

from tqdm import tqdm
from bs4 import BeautifulSoup

import settings as stt


def inspect(source_page_dir: str, disable_tqdm=False) -> Tuple[str]:
    drug_list: Set[str] = set()

    for root, _, dir_files in os.walk(source_page_dir):
        # print(f"{root=}")
        for file in tqdm(dir_files, desc='Inspecting html files', ncols=100, disable=disable_tqdm):
            if not str(file).startswith("~$") and (str(file).endswith(".html")):

                path = os.path.abspath(os.path.join(root, file))
                file_obj = codecs.open(path, encoding="utf-8")
                page_source = file_obj.read()
                file_obj.close()

                soup = BeautifulSoup(page_source, 'html5lib')
                drug = soup.find(stt.CUSTOM_DRUG_TAG).text
                drug_list.add(drug)

    return tuple(sorted(drug_list))


# if __name__ == "__main__":
#     from core.makers import inspect_by_domain
#     from icecream import ic
#     d_list = inspect_by_domain(stt.DomainKeys.LIKITEKA.name)
#     ic(d_list)
