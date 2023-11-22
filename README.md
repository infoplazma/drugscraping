# Medicament scraping

## Установка пакета

##### Domains:
 - [likiteka](https://likiteka.info)
[]()
[]()
[]()


Необходим **python** не ниже 3.10
```commandline
python3.10 -V
```

_Установка виртуального окружения_
```commandline
python3.10 -m venv venv
```

_Активировать виртуальное окружение_
```commandline
venv/Scripts/activate
```

_Установка зависимостей_
```commandline
pip install -r requirements.txt
```

Если матькнеться по поводу selenium==4.8.0 , удалит из requirements.txt и продолжить установку
без него. Затем установить отдельно
```commandline
pip install selenium==4.8.0
```

You have to select version for [undetected-chromedriver](https://pypi.org/project/undetected-chromedriver/)


[Crome for Testing availability](https://googlechromelabs.github.io/chrome-for-testing/#stable)

### Установка SpaCy

##### Installation

[spacy_russian_tokenizer: Russian segmentation and tokenization rules for spaCy](https://github.com/aatimofeev/spacy_russian_tokenizer)

-----
Скорее всего не понадобиться эта установка
```commandline
pip install git+https://github.com/aatimofeev/spacy_russian_tokenizer.git
```
##### Model installation

[Available trained pipelines for Russian](https://spacy.io/models/ru)

----
Установить последнее с **_ru_core_news_lg_**
```commandline
python -m spacy download ru_core_news_sm
python -m spacy download ru_core_news_md
python -m spacy download ru_core_news_lg
```

----
### Other articles

[Ultimate Guide To Text Similarity With Python - NewsCatcher](https://www.newscatcherapi.com/blog/ultimate-guide-to-text-similarity-with-python)

[Можно всё: решение NLP задач при помощи spacy](https://habr.com/ru/articles/531940/)

----
## Порядок работы
Активировать _виртуальное окружение_ если не активировано
```commandline
venv/Scripts/activate
```

```commandline
python manage.py --help
```

```commandline
python manage.py copy
```
Все возможные названия препаратов из excel файлов со схемой лечения из папки tasks/ будут скопированы
в файл **_tasks/task.txt_**<br>
Дальше по усмотрению можно удалить или закоментить не нужные названия.

**Скрапинг препаратов с указаного домена:**
 (_Зависит от содержимого tasks/task.txt_ !)
```commandline
python manage.py scrape <domain>

python manage.py scrape likiteka
```
Будет создан и заполнена директория data/html_source/<domain> (data/html_source/likiteka)

**Парсинг файлов после скрапинга:**
 (_Зависит от содержимого tasks/task.txt_ !)
```commandline
python manage.py parse <domain>

python manage.py parse likiteka
```
В директории data/temp/ появится файл с рапарсенными данными data/temp/domain_parsed.csv
(data/temp/likiteka_parsed.csv)

**Создание целевого файла:**
```commandline
python manage.py make <domain>

python manage.py make likiteka
```
В директории data/excel_target/ появится файл data/excel_target/domain.xlsx
(data/excel_target/likiteka.xlsx)

Если высветилось сообщение в консоле
```commandline
...
Целевой excel файл создан не будет !
Для редактирования перейти к 'drugscraping\data\unrecognizable.txt'
Aborted!
```
Открыть unrecognizable.txt и отредактировать последние значения для распознавания их в spycy.
Используя утилиту unrecognizable check "выражение"
```commandline
python .\manage.py unrecognizable -check "Аерозоль дозований"
```