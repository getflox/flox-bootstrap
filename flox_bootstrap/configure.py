from typing import Tuple

from floxcore.config import Configuration, ParamDefinition


class BootstrapConfiguration(Configuration):
    def parameters(self) -> Tuple[ParamDefinition, ...]:
        return (
            ParamDefinition("repositories", "Path to local directory or url to git repo",
                            default=["https://github.com/getflox/flox-templates.git"], multi=True),
        )

    def secrets(self) -> Tuple[ParamDefinition, ...]:
        return tuple()

    def schema(self):
        pass
