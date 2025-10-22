import logging

from clabe.launcher import Launcher, LauncherCliArgs
from pydantic_settings import CliApp

logger = logging.getLogger(__name__)


def experiment(launcher: Launcher) -> None:
    return


class ClabeCli(LauncherCliArgs):
    def cli_cmd(self):
        launcher = Launcher(settings=self)
        launcher.run_experiment(experiment)
        return None


def main() -> None:
    CliApp().run(ClabeCli)


if __name__ == "__main__":
    main()
