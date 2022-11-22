import click

from ckan import model
from .model.stat import ckanpackager_stats_table


def get_commands():
    return [ckanpackager]


@click.group()
def ckanpackager():
    """
    The CKAN Packager CLI.
    """
    pass


@ckanpackager.command(name='initdb')
def init_db():
    """
    Initialise the ckanpackager tables.
    """
    if not ckanpackager_stats_table.exists(model.meta.engine):
        ckanpackager_stats_table.create(model.meta.engine)
        click.secho('Created ckanpackager_stats table', fg='green')
    else:
        click.secho('ckanpackager_stats already exists, skipping init', fg='green')
