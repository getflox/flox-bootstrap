import click as click

from flox_bootstrap.project import enable
from floxcore.context import Flox


def _built_in_templates():
    return []


@click.command(help="Bootstrap project from template")
@click.option("--bootstrap", multiple=True)
@click.option("--no-cache", is_flag=True, default=False)
@click.pass_obj
def bootstrap_command(flox: Flox, bootstrap: tuple, no_cache: bool):
    enable(flox, bootstrap, no_cache)
