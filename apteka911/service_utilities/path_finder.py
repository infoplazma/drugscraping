import os
import settings
from pprint import pprint

REPLACE = True

text = "Септолете тотал лимон та мед льодяники по 3 мг/1 мг №16 (8х2)"
replacer_dict = {
    # 'АзитроСандоз - Порошок для оральної суспензії.': 'Азитро Сандоз пор. д/п сусп',
    # 'Окомістин  - розчин': 'Окомістин  - розчин',
    # 'Ефералгана': 'Ефералган для дітей',
    # 'Окомістін - Краплі вушні': 'Окомістин - Краплі вушні',
    # 'Окомістін - Краплі назальні': 'Окомістин - Краплі назальні',
    # 'Окомістін - Краплі очні': 'Окомістин - Краплі очні',
    # 'Окомістін - розчин': 'Окомістин - розчин',
    # 'Офтамірін - Краплі вушні': 'Офтамірин - Краплі вушні',
    # 'Офтамірін - Краплі назальні': 'Офтамірин - Краплі назальні',
    # 'Офтамірін - Краплі очні': 'Офтамірин - Краплі очні',
    # 'Офтамірін - розчин': 'Офтамірин - розчин',
    # 'Парацетамола': 'Парацетамол для дітей',
    # 'Преднізалон - таблетки.': 'Преднізолон - таблетки.'
}

for root, _, dir_files in os.walk(settings.ONE_DRIVE_DIR):
    for file in dir_files:

        if "mod_" not in file:
            path = os.path.abspath(os.path.join(root, file))

            with open(path, "r", encoding="utf-8") as fw:
                page_source = fw.read()

            # pprint(page_source)
            # print("="*120)
            if text in page_source:
                print(f"{text} found in {file}")

            mod = False
            for _old, _new in replacer_dict.items():
                if _old in page_source:
                    print(f"{_old} found in {file}")
                if REPLACE and _new not in page_source and _old in page_source:
                    page_source = page_source.replace(_old, _new)
                    mod = True

            if mod:
                path = os.path.abspath(os.path.join(root, "mod_" + file))
                with open(path, "w", encoding="utf-8") as fw:
                    fw.write(page_source)
