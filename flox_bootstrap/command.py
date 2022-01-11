import click as click

from flox_bootstrap.project import enable
from floxcore.context import Flox
from floxcore.exceptions import FloxException


def _built_in_templates():
    return []


@click.command(help="Bootstrap project from template", name="bootstrap")
@click.argument("feature", nargs=-1)
@click.option("--no-cache", is_flag=True, default=False)
@click.pass_obj
def bootstrap_command(flox: Flox, feature: tuple, no_cache: bool):
    if not flox.initiated:
        raise FloxException("Unable to bootstrap not initiated project")

    enable(flox, feature, no_cache)
