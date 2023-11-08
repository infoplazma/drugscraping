""""""
import os
from enum import Enum

from configs.init_conf import REQUIRED_COLUMN_NAMES, CONTENT_COLUMN


class DomainKeys(Enum):
    LIKITEKA = 0
    COMPENDIUM = 1
    RX = 2
    APTEKA911 = 3
    TABLETKIUA = 4


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'log')
DATA_DIR = os.path.join(BASE_DIR, 'data')
TASK_DIR = os.path.join(BASE_DIR, 'tasks')

DEFAULT_TASK_FILE_PATH = os.path.join(TASK_DIR, 'task.txt')

HTML_DATA_DIR = os.path.join(DATA_DIR, 'html_source')
EXCEL_DATA_DIR = os.path.join(DATA_DIR, 'excel_source')

# Таг добавляется в конце содраного файла для хранения url
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


# Имена колонок в excel файлах
COLUMN_NAMES = list(REQUIRED_COLUMN_NAMES) + list(CONTENT_COLUMN)

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
