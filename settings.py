""""""
import os
from enum import Enum

from configs.init_conf import REQUIRED_COLUMN_NAMES, CONTENT_COLUMN


# Ключи доменов
class DomainKeys(Enum):
    LIKITEKA = 0
    COMPENDIUM = 1
    RX = 2
    APTEKA911 = 3
    TABLETKIUA = 4


DEBUG = False

# Корневая папка проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Общие папки проекта
LOG_DIR = os.path.join(BASE_DIR, 'log')
DATA_DIR = os.path.join(BASE_DIR, 'data')
TASK_DIR = os.path.join(BASE_DIR, 'tasks')
CONFIGS_DIR = os.path.join(BASE_DIR, 'configs')
#
# Индивидуальные папки для каждого домена внутри папки DATA_DIR
HTML_DATA_DIR = os.path.join(DATA_DIR, 'html_source')
EXCEL_DATA_DIR = os.path.join(DATA_DIR, 'excel_source')
#
# Файл с перечнем имен препаратов для скрапинга и парсинга
TASK_FILE_PATH = os.path.join(TASK_DIR, 'task.txt')
#
# Файл для хранения и загрузки списка подстановок выражений форм выпуска препарата,
# которые не распознаются объектом nlp пакета spacy-ru. Описание формата и способ редактирование в заглавии файла.
UNRECOGNIZABLE_FILE_PATH = os.path.join(DATA_DIR, 'unrecognizable.log')


# Добавляемые Таги в конце соскрапленого html файла для хранения значений drug, product_name, url.
CUSTOM_DRUG_TAG = 'custom_drug'
CUSTOM_PRODUCT_NAME_TAG = 'custom_product_name'
CUSTOM_URL_TAG = 'custom_url'

# Словарь доменов
DOMAINS = {
    DomainKeys.LIKITEKA.name: 'https://likiteka.info/',
    DomainKeys.COMPENDIUM.name: 'https://compendium.com.ua/uk/',
    DomainKeys.RX.name: 'https://rx.ua/',
    DomainKeys.APTEKA911.name: 'https://apteka911.ua/ua',
    DomainKeys.TABLETKIUA.name: 'https://tabletki.ua/'}


# Имена колонок в excel файлах задаются в конфиг файле configs/init_conf.py для состыковки с базой данных.
COLUMN_NAMES = list(REQUIRED_COLUMN_NAMES) + list(CONTENT_COLUMN)

# Генерируемые значения имен колонок, если присутствуют, значит сгенерированы утилитой make_init_conf.py
IS_ADDED_COLUMNS = True
DRUG_COLUMN = 'drug'
PRODUCT_NAME_COLUMN = 'product_name'
TRADE_NAME_COLUMN = 'trade_name'
ACTIVE_INGREDIENTS_COLUMN = 'active_ingredients'
SIMPLY_RELEASE_FORM_COLUMN = 'simply_release_form'
RELEASE_FORM_COLUMN = 'release_form'
COMPOSITION_COLUMN = 'composition'
CHILDREN_COLUMN = 'children'
URL_COLUMN = 'url'
ORDER_COLUMN = 'order'
SYMPTOM_COLUMN = 'symptom'
IS_ADDED_LAST_COLUMN = True
