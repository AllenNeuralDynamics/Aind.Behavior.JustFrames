from typing import Literal, Optional

import aind_behavior_services.rig as rig
from aind_behavior_services.rig import AindBehaviorRigModel
from pydantic import BaseModel, Field, field_validator, model_validator

from . import __semver__


class NetworkConfig(BaseModel):
    address: str = Field(description="Address for ZMQ connection.")
    port: int = Field(description="Port for ZMQ connection.", ge=1, le=65535)


class SatelliteRig(AindBehaviorRigModel):
    version: Literal[__semver__] = __semver__
    zmq_protocol_config: NetworkConfig = Field(description="ZMQ connection for communication.")
    zmq_trigger_config: NetworkConfig = Field(description="ZMQ connection for trigger communication.")
    triggered_camera_controller_0: Optional[rig.cameras.CameraController[rig.cameras.SpinnakerCamera]] = Field(
        default=None,
        description="Camera controller to triggered cameras. Will use Camera0 register as a trigger.",
    )
    triggered_camera_controller_1: Optional[rig.cameras.CameraController[rig.cameras.SpinnakerCamera]] = Field(
        default=None,
        description="Camera controller to triggered cameras. Will use Camera1 register as a trigger.",
    )
    is_satellite: bool = Field(default=True)

    @field_validator("zmq_protocol_config", mode="after")
    @classmethod
    def validate_zmq_protocol_config(cls, value: rig.network.ZmqConnection):
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
    satellite_rigs: list[SatelliteRig] = Field(default_factory=list, description="List of satellite rigs.")
    is_satellite: bool = Field(default=False)
    zmq_protocol_config: NetworkConfig = Field(
        default=NetworkConfig(address="localhost", port=5555),
        description="ZMQ connection for communication.",
        validate_default=True,
    )
    zmq_trigger_config: Optional[NetworkConfig] = Field(
        default=None, description="ZMQ connection for trigger communication."
    )

    @model_validator(mode="after")
    def verify_zmq_nullability(self):
        if len(self.satellite_rigs) > 0:
            if self.zmq_trigger_config is None:
                raise ValueError("zmq_trigger_config cannot be None when satellite_rigs are defined.")
            for _r in self.satellite_rigs:
                _r.zmq_trigger_config = self.zmq_trigger_config
        return self

    @model_validator(mode="after")
    def verify_satellite_rigs(self):
        seen = set()
        for _r in self.satellite_rigs:
            if not _r.is_satellite:
                raise ValueError("All rigs in satellite_rigs must have is_satellite=True.")
            addr_port = (_r.zmq_protocol_config.address, _r.zmq_protocol_config.port)
            if addr_port in seen:
                raise ValueError(f"Duplicate address:port found in satellite_rigs: {addr_port}")
            seen.add(addr_port)
        return self
