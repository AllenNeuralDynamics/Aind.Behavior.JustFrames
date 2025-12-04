import logging
import typing as t

import pandas as pd
from contraqctor import contract, qc
from contraqctor.contract.harp import HarpDevice

from aind_behavior_just_frames.rig import AindJustFramesRig

logger = logging.getLogger(__name__)


class JustFramesQcSuite(qc.Suite):
    def __init__(self, dataset: contract.Dataset):
        self.dataset = dataset

    def test_end_session_exists(self):
        """Check that the session has an end event."""
        end_session = self.dataset["Behavior"]["Logs"]["EndSession"]

        if not end_session.has_data:
            return self.fail_test(
                None, "EndSession event does not exist. Session may be corrupted or not ended properly."
            )

        assert isinstance(end_session.data, pd.DataFrame)
        if end_session.data.empty:
            return self.fail_test(None, "No data in EndSession. Session may be corrupted or not ended properly.")
        else:
            return self.pass_test(None, "EndSession event exists with data.")


def make_qc_runner(dataset: contract.Dataset) -> qc.Runner:
    _runner = qc.Runner()
    dataset.load_all(strict=False)
    exclude: list[contract.DataStream] = []
    rig: AindJustFramesRig = dataset["Behavior"]["InputSchemas"]["Rig"].data

    # Exclude commands to Harp boards as these are tested separately
    for cmd in dataset["Behavior"]["HarpCommands"]:
        for stream in cmd:
            if isinstance(stream, contract.harp.HarpRegister):
                exclude.append(stream)

    # Add the outcome of the dataset loading step to the automatic qc
    _runner.add_suite(qc.contract.ContractTestSuite(dataset.collect_errors(), exclude=exclude), group="Data contract")

    # Add Harp tests for ALL Harp devices in the dataset
    for stream in (_r := dataset["Behavior"]):
        if isinstance(stream, HarpDevice):
            commands = t.cast(HarpDevice, _r["HarpCommands"][stream.name])
            _runner.add_suite(qc.harp.HarpDeviceTestSuite(stream, commands), stream.name)

    # Add camera qc
    for camera in dataset["BehaviorVideos"]:
        if rig.triggered_camera_controller_0 is not None and camera.name in rig.triggered_camera_controller_0.cameras:
            controller = rig.triggered_camera_controller_0
        elif rig.triggered_camera_controller_1 is not None and camera.name in rig.triggered_camera_controller_1.cameras:
            controller = rig.triggered_camera_controller_1
        else:
            logger.warning("Camera %s not found in any triggered camera controller.", camera.name)
            continue

        _runner.add_suite(
            qc.camera.CameraTestSuite(camera, expected_fps=controller.frame_rate, saturation_bounds=(1, 254)),
            camera.name,
        )

    # Add Csv tests
    csv_streams = [stream for stream in dataset.iter_all() if isinstance(stream, contract.csv.Csv)]
    for stream in csv_streams:
        _runner.add_suite(qc.csv.CsvTestSuite(stream), stream.name)

    # Add the Just Frames specific tests
    _runner.add_suite(JustFramesQcSuite(dataset), "JustFrames")

    return _runner
