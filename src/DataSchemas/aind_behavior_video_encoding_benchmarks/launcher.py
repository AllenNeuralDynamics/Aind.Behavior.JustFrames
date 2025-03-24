import logging
from pathlib import Path
from typing import final

import aind_behavior_experiment_launcher.launcher.behavior_launcher as behavior_launcher
from aind_behavior_experiment_launcher.apps import AindBehaviorServicesBonsaiApp
from aind_behavior_experiment_launcher.launcher.behavior_launcher import DefaultBehaviorPicker
from aind_behavior_experiment_launcher.resource_monitor import (
    ResourceMonitor,
    available_storage_constraint_factory,
    remote_dir_exists_constraint_factory,
)
from aind_behavior_experiment_launcher.ui import prompt_field_from_input
from aind_behavior_services.session import AindBehaviorSessionModel
from pydantic import ValidationError
from pydantic_settings import CliApp
from typing_extensions import override

from aind_behavior_video_encoding_benchmarks.rig import AindVideoEncodingBenchmarksRig
from aind_behavior_video_encoding_benchmarks.task_logic import (
    AindVideoEncodingBenchmarksTaskLogic,
    AindVideoEncodingBenchmarksTaskParameters,
)

logger = logging.getLogger(__name__)


@final
class _CustomPicker(DefaultBehaviorPicker):
    @override
    def pick_task_logic(self) -> AindVideoEncodingBenchmarksTaskLogic:
        save_raw = None
        while save_raw is None:
            try:
                save_raw = prompt_field_from_input(
                    AindVideoEncodingBenchmarksTaskParameters, "save_raw_video", default=False
                )
            except ValidationError as e:
                self.launcher._logger.error("Failed to parse input: %s", e)
            else:
                self.launcher._logger.info("save_raw_video set to: %s", save_raw)
        return AindVideoEncodingBenchmarksTaskLogic(
            task_parameters=AindVideoEncodingBenchmarksTaskParameters(save_raw_video=save_raw)
        )


def make_launcher(settings: behavior_launcher.BehaviorCliArgs) -> behavior_launcher.BehaviorLauncher:
    data_dir = settings.data_dir
    remote_dir = Path(r"\\allen\aind\scratch\video-encoding-benchmarks\data")
    srv = behavior_launcher.BehaviorServicesFactoryManager()
    srv.attach_app(AindBehaviorServicesBonsaiApp(Path(r"./src/main.bonsai")))
    srv.attach_data_transfer(behavior_launcher.robocopy_data_transfer_factory(Path(remote_dir)))
    srv.attach_resource_monitor(
        ResourceMonitor(
            constrains=[
                available_storage_constraint_factory(Path(data_dir), 2e11),
                remote_dir_exists_constraint_factory(Path(remote_dir)),
            ]
        )
    )

    return behavior_launcher.BehaviorLauncher(
        rig_schema_model=AindVideoEncodingBenchmarksRig,
        session_schema_model=AindBehaviorSessionModel,
        task_logic_schema_model=AindVideoEncodingBenchmarksTaskLogic,
        picker=_CustomPicker(
            config_library_dir=Path(r"\\allen\aind\scratch\AindBehavior.db\AindVideoEncodingBenchmarks")
        ),
        settings=settings,
        services=srv,
    )


def main():
    args = CliApp().run(behavior_launcher.BehaviorCliArgs)
    launcher = make_launcher(args)
    launcher.main()
    return None


if __name__ == "__main__":
    main()
