from typing import Literal, Optional

import aind_behavior_services.rig as rig
from aind_behavior_services.rig import AindBehaviorRigModel
from pydantic import Field

from . import __semver__


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
        ...,
        description="Harp behavior board. Will be the source of triggers for the two camera controllers.",
    )
    harp_white_rabbit: Optional[rig.harp.HarpWhiteRabbit] = Field(
        default=None, description="Harp White Rabbit for time synchronization."
    )
