"""
Добавляет константы имен колонок в settings.py
"""
import re
import click

from configs.init_conf import REQUIRED_COLUMN_NAMES

# from icecream import ic
# ic.configureOutput(includeContext=True)

IS_ADDED_COLUMNS = 'IS_ADDED_COLUMNS = True'
IS_LAST_COLUMN = 'IS_ADDED_LAST_COLUMN = True'


@click.group()
def main():
    """Синхронизация имен колонок в excel файлах с configs/excel_file_conf. Устанавливается перед использованием приложения"""


@main.command('add', short_help='Добавляет обязательные названия колонок к settings.py')
def add():
    """Add columns."""
    columns = [column.upper() + '_COLUMN = ' + f"'{column}'" for column in REQUIRED_COLUMN_NAMES]
    with open('./settings.py', 'r', encoding='utf-8') as file:
        settings_content = file.read()

    if IS_ADDED_COLUMNS in settings_content or IS_LAST_COLUMN in settings_content:
        click.secho(f"Удалить из settings.py имена колонок и затем повторить", fg='yellow')
    else:
        settings_content += IS_ADDED_COLUMNS + '\n' + '\n'.join(columns) + '\n' + IS_LAST_COLUMN
        with open('./settings.py', 'w', encoding='utf-8') as file:
            file.write(settings_content)
            click.secho('done! go to settings.py', fg='green')


@main.command('delete', short_help='Удаляет обязательные названия колонок из settings.py')
def delete_columns():
    """Deletes columns."""

    with open('./settings.py', 'r', encoding='utf-8') as file:
        settings_content = file.read()

    pattern = IS_ADDED_COLUMNS + r"[.\s\'\=\"\_\w]+" + IS_LAST_COLUMN
    settings_content = re.sub(pattern, '', settings_content)
    with open('./settings.py', 'w', encoding='utf-8') as file:
        file.write(settings_content)
        click.secho('done! go to settings.py', fg='green')


if __name__ == '__main__':
    main()
