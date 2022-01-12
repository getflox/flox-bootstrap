import click as click

from flox_bootstrap.project import enable
from floxcore.context import Flox
from floxcore.exceptions import FloxException

from loguru import logger


def _built_in_templates():
    return []


@click.command(help="Bootstrap project from template", name="bootstrap")
@click.argument("templates", nargs=-1)
@click.option("--no-cache", is_flag=True, default=False)
@click.pass_obj
def bootstrap_command(flox: Flox, templates: tuple, no_cache: bool):
    if not flox.initiated:
        raise FloxException("Unable to bootstrap not initiated project")

    command = "variables"
    variables = {}
    for name, plugin in {k: v for k, v in flox.plugins.handlers(command).items()}.items():
        for stage in plugin.handle(command, flox=flox):
            variables.update(stage.callback(flox=flox, out=logger))

    enable(flox, templates, no_cache, **variables)
