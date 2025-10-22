import logging
from pathlib import Path

from aind_behavior_services.session import AindBehaviorSessionModel
from clabe import resource_monitor
from clabe.apps import (
    AindBehaviorServicesBonsaiApp,
    BonsaiAppSettings,
)
from clabe.data_transfer import robocopy
from clabe.launcher import Launcher, LauncherCliArgs
from clabe.pickers import DefaultBehaviorPicker, DefaultBehaviorPickerSettings
from pydantic_settings import CliApp

from aind_behavior_just_frames.rig import AindJustFramesRig

logger = logging.getLogger(__name__)


def experiment(launcher: Launcher) -> None:
    monitor = resource_monitor.ResourceMonitor(
        constrains=[
            resource_monitor.available_storage_constraint_factory(launcher.settings.data_dir, 2e11),
        ]
    )

    # Validate resources
    monitor.run()

    picker = DefaultBehaviorPicker(launcher=launcher, settings=DefaultBehaviorPickerSettings())
    session = picker.pick_session(AindBehaviorSessionModel)
    launcher.register_session(session)
    rig = picker.pick_rig(AindJustFramesRig)
    bonsai_app = AindBehaviorServicesBonsaiApp(BonsaiAppSettings(workflow=Path(r"./src/main.bonsai")))
    bonsai_app.add_app_settings(launcher, rig=rig, session=session)
    bonsai_app.get_result(allow_stderr=True)

    launcher.copy_logs()
    robocopy.RobocopyService(source=launcher.session_directory, settings=robocopy.RobocopySettings())
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
