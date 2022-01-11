from click import Group

from flox_bootstrap.command import bootstrap_command
from flox_bootstrap.configure import BootstrapConfiguration
from flox_bootstrap.project import enable
from floxcore.command import Stage
from floxcore.context import Flox
from floxcore.plugin import Plugin


class BootstrapPlugin(Plugin):
    def configuration(self):
        return BootstrapConfiguration()

    def add_commands(self, cli: Group):
        cli.add_command(bootstrap_command)

    def handle_command_options_flox_project(self):
        options = (
            ("--templates", dict(help="Bootstrap project using given templates", multiple=True)),
            ("--no-cache", dict(help="Reload bootstrap template repositories", is_flag=True, default=False))
        )

        return options

    def handle_project(self, flox: Flox):
        return [
            Stage(enable, 1000)
        ]


def plugin():
    return BootstrapPlugin()
