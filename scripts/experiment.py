import asyncio
import dataclasses
import logging
from pathlib import Path

import clabe.xml_rpc
from aind_behavior_services.session import AindBehaviorSessionModel
from clabe import resource_monitor
from clabe.apps import AindBehaviorServicesBonsaiApp, BonsaiApp
from clabe.data_transfer import robocopy
from clabe.launcher import Launcher, experiment
from clabe.pickers import DefaultBehaviorPicker, DefaultBehaviorPickerSettings

from aind_behavior_just_frames import data_contract
from aind_behavior_just_frames.rig import AindJustFramesRig, SatelliteRig

logger = logging.getLogger(__name__)


@experiment(name="just_frames_with_satellites")
async def my_experiment(launcher: Launcher) -> None:
    picker = DefaultBehaviorPicker(launcher=launcher, settings=DefaultBehaviorPickerSettings())
    session = picker.pick_session(AindBehaviorSessionModel)
    rig = picker.pick_rig(AindJustFramesRig)
    launcher.register_session(session, rig.data_directory)

    monitor = resource_monitor.ResourceMonitor(
        constrains=[
            resource_monitor.available_storage_constraint_factory(launcher.data_directory, 2e11),
        ]
    )

    # Validate resources
    monitor.run()
    has_satellites = len(rig.satellite_rigs) > 0
    satellites: dict[str, SatelliteRigConnection] = {}
    if has_satellites:
        SATELLITE_UPLOAD_ROOT = "."
        for s in rig.satellite_rigs:
            xml_client = clabe.xml_rpc.XmlRpcClient(
                settings=clabe.xml_rpc.XmlRpcClientSettings(server_url=f"{s.zmq_protocol_config.address}:8000")
            )
            this_session = xml_client.upload_model(
                session, SATELLITE_UPLOAD_ROOT / f"{session.session_name}_session.json"
            )
            this_rig = xml_client.upload_model(s, SATELLITE_UPLOAD_ROOT / f"{session.session_name}_rig.json")

            assert this_session.filename is not None, "Failed to upload session to satellite rig."
            assert this_rig.filename is not None, "Failed to upload rig to satellite rig."
            additional_externalized_properties = {
                "RigPath": this_rig.filename,
                "SessionPath": this_session.filename,
            }
            satellite_bonsai_app = BonsaiApp(
                workflow=Path(r"./src/main.bonsai"),
                additional_externalized_properties=additional_externalized_properties,
            )
            satellites[s.rig_name] = SatelliteRigConnection(
                rig=s,
                xml_rpc_client=xml_client,
                bonsai_app=satellite_bonsai_app,
                xml_rpc_executor=clabe.xml_rpc.XmlRpcExecutor(client=xml_client),
            )

    bonsai_app = AindBehaviorServicesBonsaiApp(
        workflow=Path(r"./src/main.bonsai"),
        rig=rig,
        session=session,
    )

    tasks = {
        satellite.rig.rig_name: satellite.xml_rpc_executor.run_async(satellite.bonsai_app.command)
        for satellite in satellites.values()
    }
    tasks[rig.rig_name] = bonsai_app.run_async()
    results = await asyncio.gather(*tasks.values())

    for rig_id, result in dict(zip(tasks.keys(), results)).items():
        if result.exit_code != 0:
            logger.error(
                "RigId %s 's, App exited with error code %d. With stdout %s and stderr %s",
                rig_id,
                result.exit_code,
                result.stdout,
                result.stderr,
            )
        else:
            logger.info("RigId %s 's, App completed successfully with stdout %s", rig_id, result.stdout)
            logger.debug("RigId %s 's, App completed successfully with stderr %s", rig_id, result.stderr)

    # Run data qc
    if picker.ui_helper.prompt_yes_no_question("Would you like to generate a qc report?"):
        try:
            import webbrowser

            from contraqctor.qc.reporters import HtmlReporter

            from ..src.aind_behavior_just_frames.data_qc.data_qc import make_qc_runner

            _dataset = data_contract.dataset(launcher.session_directory)
            runner = make_qc_runner(_dataset)
            qc_path = launcher.session_directory / "Behavior" / "Logs" / "qc_report.html"
            reporter = HtmlReporter(output_path=qc_path)
            runner.run_all_with_progress(reporter=reporter)
            webbrowser.open(qc_path.as_uri(), new=2)
        except Exception as e:
            logger.error("Failed to run data QC: %s", e)

    launcher.copy_logs()
    settings = robocopy.RobocopySettings()
    settings.destination = Path(settings.destination) / launcher.session.subject / launcher.session.session_name
    robocopy.RobocopyService(source=launcher.session_directory, settings=settings).transfer()
    return


@dataclasses.dataclass
class SatelliteRigConnection:
    rig: SatelliteRig
    xml_rpc_client: clabe.xml_rpc.XmlRpcClient
    xml_rpc_executor: clabe.xml_rpc.XmlRpcExecutor
    bonsai_app: BonsaiApp
