import datetime
import os

import aind_behavior_services.rig as rig

from aind_behavior_services.session import AindBehaviorSessionModel

from aind_behavior_just_frames.rig import AindJustFramesRig


def main(path_seed: str = "./local/{schema}.json"):
    this_session = AindBehaviorSessionModel(
        date=datetime.datetime.now(tz=datetime.timezone.utc),
        experiment="AindVideoEncodingBenchmarks",
        root_path="c://",
        subject="Test",
        notes="test session",
        experiment_version="0.0.0",
        allow_dirty_repo=False,
        skip_hardware_validation=False,
        experimenter=["Foo", "Bar"],
    )

    video_writer = rig.cameras.VideoWriterFfmpeg(
        frame_rate=120,
        container_extension="mp4",
        # input and output arguments can be overridden by the user
    )

    this_rig = AindJustFramesRig(
        rig_name="this_rig",
        triggered_camera_controller_0=rig.cameras.CameraController[rig.cameras.SpinnakerCamera](
            frame_rate=120,
            cameras={
                "FaceCamera": rig.cameras.SpinnakerCamera(
                    serial_number="SerialNumber",
                    binning=1,
                    exposure=5000,
                    gain=0,
                    video_writer=video_writer,
                    adc_bit_depth=rig.cameras.SpinnakerCameraAdcBitDepth.ADC10BIT,
                ),
                "SideCamera": rig.cameras.SpinnakerCamera(
                    serial_number="SerialNumber",
                    binning=1,
                    exposure=5000,
                    gain=0,
                    video_writer=video_writer,
                    adc_bit_depth=rig.cameras.SpinnakerCameraAdcBitDepth.ADC10BIT,
                ),
            },
        ),
        triggered_camera_controller_1=None,
        harp_behavior=rig.harp.HarpBehavior(port_name="COM3"),
    )

    os.makedirs(os.path.dirname(path_seed), exist_ok=True)

    models = [this_session, this_rig]

    for model in models:
        with open(path_seed.format(schema=model.__class__.__name__), "w", encoding="utf-8") as f:
            f.write(model.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
