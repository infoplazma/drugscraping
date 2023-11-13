"""
Click Documenting Scripts:
https://click.palletsprojects.com/en/8.1.x/documentation/
"""
import pprint
import click

from core.maker_lib.full_task_file_maker import fill_drugs
from core.makers import make_parsing, make_scraping
from core.utilities import read_log
from settings import DOMAINS
import settings as stt


PROCESSES = ['scrape', 'parse', 'copy']
DOMAIN_LIST = " ".join(DOMAINS.keys())


@click.command(epilog=f"Task files in ./tasks/*. Result in dir ./data Log files in dir ./log")
@click.argument("process")
@click.argument("domain", default='')
@click.option('-n', type=int, default=-1, help='количество выводимых препаратов')
def main(process: str, domain, n):
    """Simple program that make process in PROCESS domain by DOMAIN:

    PROCESS:

        show - показать содержимое файла 'задание'

        copy - копирует название всех препаратов в файл 'задание'

        scrape - скрепит заданный домен

        parse- парсит собранные данные с домена

    DOMAIN:

        - likiteka

        - compendium

        - rx

        - apteka911

        - tabletkiua"""

    cmd = {process: domain, 'n': n}

    match cmd:
        case {'scrape': str(x)} if x.upper() in DOMAIN_LIST:
            click.secho(f"Starting scraping {x}", fg='green')
            make_scraping(domain)

        case {'parse': str(x)} if x.upper() in DOMAIN_LIST:
            click.secho(f"Starting parsing {x}", fg='green')
            make_parsing(domain)

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

        case _:
            click.secho('Неверная команда', fg='red')


if __name__ == "__main__":
    main()
