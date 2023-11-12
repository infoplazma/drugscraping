"""
Click Documenting Scripts:
https://click.palletsprojects.com/en/8.1.x/documentation/
"""
import click
from settings import DOMAINS
from core.makers import make_scraping

domain_list = " ".join(DOMAINS.keys())


@click.command(epilog=f"Result in dir ./data, log files in dir ./log")
@click.argument("domainkey")
def main(domainkey):
    """Simple program that scraping domain by DOMAINKEY:

    - likiteka

    - compendium

    - rx

    - apteka911

    - tabletkiua"""

    if domainkey.upper() not in DOMAINS:
        click.secho(f"Not found {domainkey} in {domain_list.split(' ')}", fg='red')
        exit(-1)
    click.secho(f"domain:{DOMAINS[domainkey.upper()]}", fg='green')
    make_scraping(domainkey.upper())


if __name__ == '__main__':
    main()
