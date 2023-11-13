import settings as stt
from core.excel_maker import ExcelMaker
from core.utilities import is_open_file


def fill_drugs(task_dir: str, task_file_path: str) -> list:
    """
    Заливает все названия препаратов из схемы лечения в /tasks/task.txt
    """
    if is_open_file(task_file_path):
        exit()

    maker = ExcelMaker()
    print("Загрузка файлов с схемой лечения...")
    maker.load(task_dir, columns=stt.SCHEME_COLUMN_MAPPER)
    with open(task_file_path, 'w', encoding='utf-8') as file:
        for drug in maker.drug_list:
            file.write(drug + "\n")

    return maker.drug_list


if __name__ == "__main__":
    from core.utilities import read_log
    from icecream import ic
    # fill_drugs(stt.TASK_DIR, stt.TASK_FILE_PATH)

    ic(read_log(stt.TASK_FILE_PATH))
