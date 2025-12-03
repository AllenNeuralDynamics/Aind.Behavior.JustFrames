import typing as t

from pydantic import Field, RootModel
from pydantic_settings import BaseSettings, CliApp, CliSubCommand

from aind_behavior_just_frames import __semver__, regenerate
from aind_behavior_just_frames.data_qc import DataQcCli
from aind_behavior_just_frames.launcher import ClabeCli


class VersionCli(RootModel):
    root: t.Any

    def cli_cmd(self) -> None:
        print(__semver__)


class DslRegenerateCli(RootModel):
    root: t.Any

    def cli_cmd(self) -> None:
        regenerate.main()


class JustFramesCli(BaseSettings, cli_prog_name="just-frames", cli_kebab_case=True):
    version: CliSubCommand[VersionCli] = Field(
        description="Print the version of the just-frames package.",
    )
    data_qc: CliSubCommand[DataQcCli] = Field(description="Run data quality checks.")
    regenerate: CliSubCommand[DslRegenerateCli] = Field(
        description="Regenerate the just-frames dsl dependencies.",
    )
    clabe: CliSubCommand[ClabeCli] = Field(
        description="Run the Clabe CLI.",
    )

    def cli_cmd(self):
        return CliApp().run_subcommand(self)


def main():
    CliApp().run(JustFramesCli)


if __name__ == "__main__":
    main()
