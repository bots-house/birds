import asyncio
import click
import os
from datetime import datetime, timezone

from birds.migrator import MigrationDirection, Migrator


@click.group()
def cli():
    pass

@click.command()
@click.argument("name")
@click.option("--dir", default="migrations", help="migrations location")
def new(name: str, dir: str):
    if not os.path.isdir(dir):
        os.makedirs(dir)

    now = datetime.now(timezone.utc)
    filename_template = "{dir}/{timestamp}_{name}.{type}.sql"

    open(filename_template.format(dir=dir, timestamp=int(now.timestamp()), name=name, type="up"), "w")
    open(filename_template.format(dir=dir, timestamp=int(now.timestamp()), name=name, type="down"), "w")


@click.command()
@click.option("--db_url", help="pg database url; postgres://..")
@click.option("--dir", default="migrations", help="migrations location")
@click.option("--count", default=-1, help="migrations count to upgrade")
def up(db_url: str, dir: str, count: int):
    migrator = Migrator(dir=dir, db_url=db_url)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(migrator.apply_migrations(direction=MigrationDirection.UP, count=count))


@click.command()
@click.option("--db_url", help="pg database url; postgres://..")
@click.option("--dir", default="migrations", help="migrations location")
@click.option("--count", default=-1, help="migrations count to downgrade")
def down(db_url: str, dir: str, count: int):
    migrator = Migrator(dir=dir, db_url=db_url)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(migrator.apply_migrations(direction=MigrationDirection.DOWN, count=count))


if __name__ == "__main__":
    cli.add_command(new)
    cli.add_command(up)
    cli.add_command(down)
    cli()
