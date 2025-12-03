from typing import Literal, Optional

import aind_behavior_services.rig as rig
from aind_behavior_services.rig import AindBehaviorRigModel
from pydantic import BaseModel, Field, field_validator, model_validator

from . import __semver__


class ZmqPubSub(BaseModel):
    pub: rig.network.ZmqConnection = Field(description="ZMQ Publisher")
    sub: rig.network.ZmqConnection = Field(description="ZMQ Subscriber")


class SatelliteRig(AindBehaviorRigModel):
    version: Literal[__semver__] = __semver__
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
        default_factory=list, description="List of satellite rigs."
    )
    is_satellite: bool = Field(default=False)
    zmq_connection: Optional[ZmqPubSub] = Field(default=None, description="ZMQ connection for communication.")

    @model_validator(mode="after")
    def verify_zmq_nullability(self):
        if self.zmq_connection is None:
            if self.is_satellite:
                raise ValueError("Satellite rigs must define a ZMQ connection.")
            if len(self.satellite_rigs) > 0:
                raise ValueError("Master rigs with satellite rigs must define a ZMQ connection.")
        return self

    @model_validator(mode="after")
    def verify_satellite_rigs(self):
        for _r in self.satellite_rigs:
            if not _r.is_satellite:
                raise ValueError("All rigs in satellite_rigs must have is_satellite=True.")
        return self
