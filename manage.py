"""
Click Documenting Scripts:
https://click.palletsprojects.com/en/8.1.x/documentation/
"""
import pprint
import click

from core.maker_lib.full_task_file_maker import fill_drugs
from core.makers import make_parsing, make_scraping, make_inspecting, add_unrecognizable_to_list, check_release_form, \
    make_target_file
from core.utilities import read_log
from settings import DOMAINS
import settings as stt


PROCESSES = ['scrape', 'parse', 'copy']
DOMAIN_LIST = " ".join(DOMAINS.keys())


@click.command(epilog=f"Task files in ./tasks/*. Result in dir ./data Log files in dir ./log")
@click.argument("process")
@click.argument("domain", default='')
@click.option('-n', type=int, default=-1, help='количество выводимых препаратов')
@click.option('-add', type=str, default='', help='добавляемая форма выпуска препарата')
@click.option('-check', type=str, default='', help='проверяемая форма выпуска препарата')
def main(process: str, domain, n, add, check):
    """Simple program that make process in PROCESS domain by DOMAIN:

    PROCESS:

        scrape - скрепит заданный домен, обязательный аргумент имя domain

        parse - парсит собранные данные с домена, обязательный аргумент имя domain

        make - создает целевой excel файл для домена, обязательный аргумент имя domain

        inspect - проверяет какие перепараты соскрепленны для конкретного домена, обязательный аргумент имя domain

        show - показать список препаратов из файла 'задание'

        copy - копирует из схемы лечения название всех препаратов в файл 'задание'

        unrecognizable - показывает, проверяет и добавляет не распознаваемые выражение формы выпуска препарата для пакета spacy.
        Для проверки указывать опцию: -check 'форма выпуска препарата'
        Для добавления указывать опцию: -add 'форма выпуска препарата'

        filter - отфильтровывает из целевого файла значения из заданого списка

    DOMAIN:

        - likiteka

        - compendium

        - rx

        - apteka911

        - tabletkiua"""

    cmd = {process: domain, 'n': n, 'add': add, 'check': check}

    match cmd:
        case {'scrape': str(x)} if x.upper() in DOMAIN_LIST:
            click.secho(f"\nStart scraping domain: '{x}'", fg='green')
            make_scraping(domain)

        case {'parse': str(x)} if x.upper() in DOMAIN_LIST:
            click.secho(f"\nStart parsing domain's html files: '{x}'", fg='green')
            make_parsing(domain)

        case {'make': str(x)} if x.upper() in DOMAIN_LIST:
            click.secho(f"\nStart making target excel file: '{x}'", fg='green')
            make_target_file(domain)

        case {'inspect': str(x)} if x.upper() in DOMAIN_LIST:
            click.secho(f"\nStart inspecting domain: '{x}'", fg='green')
            click.echo(pprint.pformat(make_inspecting(domain)) + '\n')

        case {'show': '', 'n': -1}:
            drug_tusk_list = read_log(stt.TASK_FILE_PATH)
            click.echo(pprint.pformat(drug_tusk_list))
            click.secho(f"В файл:'{stt.TASK_FILE_PATH}'\n", fg='green')

        case {'show': '', 'n': int(n)} if n > 0:
            drug_tusk_list = read_log(stt.TASK_FILE_PATH)
            click.secho(f"Препаратов {len(drug_tusk_list)}:\n", fg='green')
            click.secho(pprint.pformat(drug_tusk_list[:n]), fg='green')
            click.secho(f"В файл:'{stt.TASK_FILE_PATH}'\n", fg='green')

        case {'copy': ''}:
            drug_tusk_list = fill_drugs(stt.TASK_DIR, stt.TASK_FILE_PATH)
            click.secho(f"Скопировано {len(drug_tusk_list)} препаратов в файл: {stt.TASK_FILE_PATH}", fg='green')

        case {'unrecognizable': '', 'add': '', 'check': ''}:
            unrecognizable_list = add_unrecognizable_to_list()
            click.echo(pprint.pformat(unrecognizable_list, indent=3))
            click.echo(f"Для редактирования: '{stt.UNRECOGNIZABLE_FILE_PATH}'\n")

        case {'unrecognizable': '', 'add': str(x)} if x:
            click.secho(f"\nStart adding: '{x}'", fg='green')
            add_unrecognizable_to_list(add)
            click.echo(f"Для редактирования открыть: '{stt.UNRECOGNIZABLE_FILE_PATH}'\n")

        case {'unrecognizable': '', 'check': str(x)} if x:
            click.secho(f"\nStart checking: '{x}'", fg='green')
            click.echo(f"Для редактирования открыть: '{stt.UNRECOGNIZABLE_FILE_PATH}'\n")
            check_release_form(check)


        case _:
            click.secho('Неверная команда', fg='red')


if __name__ == "__main__":
    main()
