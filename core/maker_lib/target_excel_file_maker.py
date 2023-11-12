import os
from pprint import pprint
import pandas as pd
from colorama import Fore, Style
# from icecream import ic

import settings as stt

from core.utilities import save_log, dfs_to_excel, is_open_file, make_dir_in_log_dir
from core.excel_maker import ExcelMaker
from core.similarity import Substitution, save_unrecognizable, read_substitution_list, get_nlp


def make_target_excel_file(temp_file_path: str, target_excel_file_path: str):

    if is_open_file(target_excel_file_path):
        exit()
    if is_open_file(temp_file_path):
        exit()

    # Читаем временный файл с распарсенными данными
    df_parsed = pd.read_csv(temp_file_path)
    # Удаляем временный файл
    os.remove(temp_file_path)
    df_parsed.dropna(subset=[stt.DRUG_COLUMN, stt.RELEASE_FORM_COLUMN], inplace=True)

    # Загружаем лингвистическую модель
    nlp = get_nlp(model=stt.SPACY_MODEL)

    # Создаем экземпляр класса подстановок Substitution
    if os.path.isfile(stt.UNRECOGNIZABLE_FILE_PATH):
        substitution_list = read_substitution_list(stt.UNRECOGNIZABLE_FILE_PATH)
        print(f"Данные для подстановок прочитаны из '{stt.UNRECOGNIZABLE_FILE_PATH}'")
        substitution = Substitution(substitution_list)
    else:
        substitution = None

    # Создаем экземпляр класса ExcelMaker
    maker = ExcelMaker(nlp=nlp, substitution=substitution)
    # Загружаем данные схем лечения
    print("Загрузка файлов с схемой лечения...")
    maker.load(stt.TASK_DIR, columns={"#": stt.ORDER_COLUMN,
                                      "Симптом": stt.SYMPTOM_COLUMN,
                                      "Препарат": stt.DRUG_COLUMN,
                                      "Форма выпуска": stt.RELEASE_FORM_COLUMN})

    # Проверяем наличие не распознанных выражений форм выпуска препаратов
    unrecognizable_list = maker.check_model(df_parsed)

    if unrecognizable_list:
        save_unrecognizable(stt.UNRECOGNIZABLE_FILE_PATH, unrecognizable_list, nlp)
        print(f"Обнаружено {len(unrecognizable_list)} нераспознаваемых выражений:")
        pprint(unrecognizable_list)
        print(f"\nДля редактирования перейти к \n'{stt.UNRECOGNIZABLE_FILE_PATH}'")
    else:
        # Создаем файл для загрузки в базу данных
        print("Создание excel файла для загрузки в базу данных...")
        dfs, refused = maker.make(df_parsed=df_parsed, threshold=stt.RELEASE_FORM_THRESHOLD)

        # Проверяем результат
        if len(dfs) == 0:
            print(Fore.RED + Style.BRIGHT + "Не удалось найти ни один подходящий препарат.", end='')
            print(Style.RESET_ALL)
            exit()

        make_dir_in_log_dir(stt.EXCEL_DATA_DIR)
        dfs_to_excel(target_excel_file_path,
                     dfs,
                     highlighted_columns=[stt.ORDER_COLUMN, stt.SYMPTOM_COLUMN,
                                          'Спосіб застосування та дози', stt.URL_COLUMN])
        print(f"Excel файл создан и сохранен '{target_excel_file_path}'")

        log_path = os.path.join(stt.LOG_DIR, stt.DomainKeys.LIKITEKA.name.lower(), 'release-form-similarity.log')
        save_log(log_path, refused)
        print(f"Лог файл с отклоненными записями сохранен '{log_path}'")

        if not refused:
            print('Не обнаружено отклоненных записей')


if __name__ == "__main__":
    temp_file_path = os.path.join(stt.TEMP_DATA_DIR, stt.DomainKeys.LIKITEKA.name.lower() + "_parsed.csv")
    # Путь куда будет сохранен файл
    target_excel_file_path = os.path.join(stt.EXCEL_DATA_DIR, stt.DomainKeys.LIKITEKA.name.lower() + ".xlsx")
    make_target_excel_file(temp_file_path, target_excel_file_path)

