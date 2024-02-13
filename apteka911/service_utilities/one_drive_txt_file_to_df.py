"""
Трансформирует из папки settings.ONE_DRIVE_DIR файлы в таблицу pd.DataFrame с колонками
"diagnosis", "symptom", "sub_symptom", "drug", "release_form"
"""
from typing import Tuple, List, Dict
import re
from pathlib import Path

import pandas as pd

import settings
from core.utilities import get_file_path_list, read_log

RELEASE_FORMS = "Краплі+очні Краплі+вушні Краплі+назальні Краплі+оральні Краплі Таблетки розчин Сироп порошок " \
                "суспензія+оральна суспензія Розчин+оральний Розчин Спрей сіль гель капсули льодяники аерозоль пастилки"


def transform_to_df(path_dir: str) -> pd.DataFrame:
    """
    Трансформирует из папки settings.ONE_DRIVE_DIR файлы в таблицу с колонками
    "diagnosis", "symptom", "sub_symptom", "drug", "release_form"
    """
    contents = read_contents(path_dir)
    contents = separate(contents)
    return to_df(contents)


def read_contents(path_dir: str) -> Dict[str, List[str]]:
    file_path_list = get_file_path_list(path_dir)
    content_list = {Path(path).stem.strip().capitalize(): read_log(path) for path in file_path_list}
    return content_list


def separate(contents: Dict[str, List[str]]) -> Dict[str, List[Tuple[int, int, str, str]]]:
    new_contents = dict()
    release_form_patterns = [rf.lower().replace("+", " ") for rf in RELEASE_FORMS.split()]
    for diagnosis, doc in contents.items():
        index = symptom_index = 0
        content = []
        for sentence in doc:
            sentence = re.sub(r"\s+", " ", sentence).strip()
            match = re.match(r"^(\d+).+(\d+)?", sentence)
            if match:
                match_symptom = re.search(r"\d+.+(\d+)", match.string)
                if match_symptom:
                    symptom_index = int(match_symptom.group(1))
                else:
                    symptom_index = 0
                index = int(match.group(1))
                # print(match.string, "=>",  index, " ", symptom_index, "  -", diagnosis)
            else:
                content.append((index, symptom_index, sentence, get_release_form(sentence, release_form_patterns)))

        new_contents[diagnosis] = content

    return new_contents


def to_df(contents: Dict[str, List[Tuple[int, int, str, str]]]) -> pd.DataFrame:
    con_list: List[Tuple[str, int, int, str, str]] = []
    for diagnosis, records in contents.items():
        for record in records:
            con_list.append((diagnosis, *record))
    return pd.DataFrame(con_list, columns=["diagnosis", "symptom", "sub_symptom", "drug", "release_form"])


def get_release_form(sentence: str, patterns: List[str]) -> str | None:
    release_form = ""
    for pattern in patterns:
        if re.search(pattern, sentence, flags=re.I):
            release_form += pattern + " "

    release_form = " ".join(set(release_form.split()))
    return release_form.strip()


if __name__ == "__main__":
    from pprint import pprint

    # pprint(separate(read_contents(settings.ONE_DRIVE_DIR)))
    df = transform_to_df(settings.ONE_DRIVE_DIR)
    drug_list = sorted(df["drug"].unique())
    # print(*drug_list, sep="\n")
    print(f"{len(drug_list)=}")

    pprint(df.to_records(index=False))

