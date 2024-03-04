"""
Осуществляет поиск и замену при REPLACE = True в settings.ONE_DRIVE_DIR
"""
import os
import settings
from pprint import pprint


def search_replace(search_text: str, replacer_dict=dict(), replace: bool = False):
    for root, _, dir_files in os.walk(settings.ONE_DRIVE_DIR):
        for file in dir_files:

            if "mod_" not in file:
                path = os.path.abspath(os.path.join(root, file))

                with open(path, "r", encoding="utf-8") as fw:
                    page_source = fw.read()

                # pprint(page_source)
                # print("="*120)
                if search_text in page_source:
                    print(f"{search_text} found in '{file}'")

                mod = False
                for _old, _new in replacer_dict.items():
                    if _old in page_source:
                        print(f"{_old} found in '{file}'")
                    if replace and _new not in page_source and _old in page_source:
                        page_source = page_source.replace(_old, _new)
                        mod = True

                if mod:
                    path = os.path.abspath(os.path.join(root, "mod_" + file))
                    with open(path, "w", encoding="utf-8") as fw:
                        fw.write(page_source)


if __name__ == "__main__":
    # Строка поиска
    search_text_ = "Себідин"

    # Флаг и словарь для замены, при флаге REPLACE = False проводит поиск по ключам в словаре без замен
    REPLACE = False
    replacer_dict_ = {
        "Себідин таблетки д/розсмок. №20": ""
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

    search_replace(search_text_, replacer_dict_)