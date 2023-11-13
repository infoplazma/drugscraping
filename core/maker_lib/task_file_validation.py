"""
Проверка на валидность перечня лекарств из файла /tasks/task.txt
"""
from pprint import pprint
from typing import Tuple

from colorama import Fore, Style

import settings as stt
from core.excel_maker import ExcelMaker
from core.utilities import read_log


def validate_task_list(task_dir: str, task_file_path: str) -> Tuple[str]:
    """
    Возвращает название препаратов из файла /tasks/task.txt которые не найдены в заданной схеме лечения /tasks/*.xlsx.
    """
    maker = ExcelMaker()
    print("Загрузка файлов с схемой лечения...")
    maker.load(task_dir, columns=stt.SCHEME_COLUMN_MAPPER)

    drug_tusk_list = read_log(task_file_path)
    if not drug_tusk_list:
        raise ValueError(f"Не найдены валидные названия препаратов в файле:'{task_file_path}'")
    return tuple(set(drug_tusk_list).difference(set(maker.drug_list)))


def validate_task_file():
    err_list = validate_task_list(stt.TASK_DIR, stt.TASK_FILE_PATH)
    if err_list:
        print(Fore.RED + Style.BRIGHT + f"Обнаружены названия препаратов не найденные в схеме лечения:\n", end='')
        pprint(err_list)
        print(f"Отредактируйте содержимое файла {stt.TASK_FILE_PATH}")
        print(Fore.YELLOW + Style.BRIGHT + "\n...terminated")
        print(Style.RESET_ALL)
        exit()


if __name__ == "__main__":
    from icecream import ic
    ic(validate_task_list(stt.TASK_DIR, stt.TASK_FILE_PATH))
    validate_task_file()


