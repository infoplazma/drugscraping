"""
Click Documenting Scripts:
https://click.palletsprojects.com/en/8.1.x/documentation/
"""
import pprint
import click

from core.maker_lib.full_task_file_maker import fill_drugs
from core.makers import make_parsing, make_scraping, make_inspecting, make_unrecognizable
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
def main(process: str, domain, n, add):
    """Simple program that make process in PROCESS domain by DOMAIN:

    PROCESS:

        scrape - скрепит заданный домен, обязательный аргумент имя domain

        parse- парсит собранные данные с домена, обязательный аргумент имя domain

        inspect - проверяет какие перепараты соскрепленны для конкретного домена, обязательный аргумент имя domain

        show - показать список препаратов из файла 'задание'

        copy - копирует из схемы лечения название всех препаратов в файл 'задание'

        unrecognizable - показывает и добавляет не распознаваемые выражение формы выпуска препарата для пакета spacy.
        Для добавления указывать опцию: -add 'форма выпуска препарата'

    DOMAIN:

        - likiteka

        - compendium

        - rx

        - apteka911

        - tabletkiua"""

    cmd = {process: domain, 'n': n, 'add': add}

    match cmd:
        case {'scrape': str(x)} if x.upper() in DOMAIN_LIST:
            click.secho(f"\nStart scraping domain: '{x}'", fg='green')
            make_scraping(domain)

        case {'parse': str(x)} if x.upper() in DOMAIN_LIST:
            click.secho(f"\nStart parsing domain: '{x}'", fg='green')
            make_parsing(domain)

        case {'inspect': str(x)} if x.upper() in DOMAIN_LIST:
            click.secho(f"\nStart inspecting domain: '{x}'", fg='green')
            click.echo(pprint.pformat(make_inspecting(domain)) + '\n')

        case {'show': '', 'n': -1}:
            drug_tusk_list = read_log(stt.TASK_FILE_PATH)
            click.secho(pprint.pformat(drug_tusk_list), fg='green')

        case {'show': '', 'n': int(n)} if n > 0:
            drug_tusk_list = read_log(stt.TASK_FILE_PATH)
            click.secho(f"Препаратов {len(drug_tusk_list)}:\n", fg='green')
            click.secho(pprint.pformat(drug_tusk_list[:n]), fg='green')
            click.secho(f"В файл:'{stt.TASK_FILE_PATH}'", fg='green')

        case {'copy': ''}:
            drug_tusk_list = fill_drugs(stt.TASK_DIR, stt.TASK_FILE_PATH)
            click.secho(f"Скопировано {len(drug_tusk_list)} препаратов в файл: {stt.TASK_FILE_PATH}", fg='green')

        case {'unrecognizable': '', 'add': ''}:
            unrecognizable_list = make_unrecognizable()
            click.echo(pprint.pformat(unrecognizable_list, indent=3))
            click.echo(f"Для редактирования: '{stt.UNRECOGNIZABLE_FILE_PATH}'\n")

        case {'unrecognizable': '', 'add': str(x)} if x:
            click.secho(f"\nStart adding: '{x}'", fg='green')
            make_unrecognizable(add)
            click.echo(f"Для редактирования открыть: '{stt.UNRECOGNIZABLE_FILE_PATH}'\n")

        case _:
            click.secho('Неверная команда', fg='red')


if __name__ == "__main__":
    main()
