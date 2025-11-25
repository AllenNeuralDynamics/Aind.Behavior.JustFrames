from typing import Literal, Optional

import aind_behavior_services.rig as rig
from aind_behavior_services.rig import AindBehaviorRigModel
from pydantic import BaseModel, Field, field_validator

from . import __semver__


class ZmqPubSub(BaseModel):
    pub: rig.network.ZmqConnection = Field(description="ZMQ Publisher")
    sub: rig.network.ZmqConnection = Field(description="ZMQ Subscriber")

class SatelliteRig(AindBehaviorRigModel):
    version: Literal[__semver__] = __semver__
    computer_name: str = Field(description="Remote Computer name")
    zmq_connection: ZmqPubSub = Field(description="ZMQ connection for communication.")
    triggered_camera_controller_0: Optional[rig.cameras.CameraController[rig.cameras.SpinnakerCamera]] = Field(
        default=None,
        description="Camera controller to triggered cameras. Will use Camera0 register as a trigger.",
    )
    triggered_camera_controller_1: Optional[rig.cameras.CameraController[rig.cameras.SpinnakerCamera]] = Field(
        default=None,
        description="Camera controller to triggered cameras. Will use Camera1 register as a trigger.",
    )
    is_satellite: bool = Field(default=True)

    @field_validator("zmq_connection", mode="after")
    @classmethod
    def validate_zmq_connection(cls, value: rig.network.ZmqConnection):
        if isinstance(value, rig.network.ZmqConnection):
            value.topic = ""
        return value


class AindJustFramesRig(AindBehaviorRigModel):
    version: Literal[__semver__] = __semver__
    triggered_camera_controller_0: Optional[rig.cameras.CameraController[rig.cameras.SpinnakerCamera]] = Field(
        default=None,
        description="Camera controller to triggered cameras. Will use Camera0 register as a trigger.",
    )
    triggered_camera_controller_1: Optional[rig.cameras.CameraController[rig.cameras.SpinnakerCamera]] = Field(
        default=None,
        description="Camera controller to triggered cameras. Will use Camera1 register as a trigger.",
    )
    harp_behavior: rig.harp.HarpBehavior = Field(
        description="Harp behavior board. Will be the source of triggers for the two camera controllers.",
    )
    satellite_rigs: list[SatelliteRig] = Field(
        default_factory=list, min_length=1, description="List of satellite rigs."
    )
    is_satellite: bool = Field(default=False)
    zmq_connection: ZmqPubSub = Field(description="ZMQ connection for communication.")
