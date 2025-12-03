import logging
from pathlib import Path

from aind_behavior_services.session import AindBehaviorSessionModel
from clabe import resource_monitor
from clabe.apps import (
    AindBehaviorServicesBonsaiApp,
)
from clabe.data_transfer import robocopy
from clabe.launcher import Launcher, LauncherCliArgs
from clabe.pickers import DefaultBehaviorPicker, DefaultBehaviorPickerSettings
from pydantic_settings import CliApp

from aind_behavior_just_frames import data_contract
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
    rig = picker.pick_rig(AindJustFramesRig)
    launcher.register_session(session, rig.data_directory)
    bonsai_app = AindBehaviorServicesBonsaiApp(
        workflow=Path(r"./src/main.bonsai"),
        rig=rig,
        session=session,
    )
    bonsai_app.run()

    # Run data qc
    if picker.ui_helper.prompt_yes_no_question("Would you like to generate a qc report?"):
        try:
            import webbrowser

            from contraqctor.qc.reporters import HtmlReporter

            from .data_qc.data_qc import make_qc_runner

            _dataset = data_contract.dataset(launcher.session_directory)
            runner = make_qc_runner(_dataset)
            qc_path = launcher.session_directory / "Behavior" / "Logs" / "qc_report.html"
            reporter = HtmlReporter(output_path=qc_path)
            runner.run_all_with_progress(reporter=reporter)
            webbrowser.open(qc_path.as_uri(), new=2)
        except Exception as e:
            logger.error("Failed to run data QC: %s", e)

    launcher.copy_logs()
    robocopy.RobocopyService(source=launcher.session_directory, settings=robocopy.RobocopySettings()).transfer()
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
