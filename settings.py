""""""
import os
from enum import Enum


class DomainKeys(Enum):
    LIKITEKA = 0
    COMPENDIUM = 1
    RX = 2
    APTEKA911 = 3
    TABLETKIUA = 4


DOMAINS = {
    DomainKeys.LIKITEKA.name: 'https://likiteka.info/',
    DomainKeys.COMPENDIUM.name: 'https://compendium.com.ua/uk/',
    DomainKeys.RX.name: 'https://rx.ua/',
    DomainKeys.APTEKA911.name: 'https://apteka911.ua/ua',
    DomainKeys.TABLETKIUA.name: 'https://tabletki.ua/'}

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'log')
DATA_DIR = os.path.join(BASE_DIR, 'data')
TASK_DIR = os.path.join(BASE_DIR, 'tasks')

DEFAULT_TASK_FILE_PATH = os.path.join(TASK_DIR, 'task.txt')

HTML_DATA_DIR = os.path.join(DATA_DIR, 'html_source')

# Таг добавляется в конце содраного файла для хранения url
CUSTOM_DRUG_TAG = 'custom_drug'
CUSTOM_PRODUCT_NAME_TAG = 'custom_product_name'
CUSTOM_URL_TAG = 'custom_url'

