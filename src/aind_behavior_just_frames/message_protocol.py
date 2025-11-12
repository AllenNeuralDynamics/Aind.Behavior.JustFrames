from typing import Annotated, Any, Literal, Union

from aind_behavior_services.message_protocol import HeartbeatPayload, LogPayload, _Message
from aind_behavior_just_frames.rig import SatelliteRig
from aind_behavior_services.session import AindBehaviorSessionModel
from pydantic import BaseModel, ConfigDict, Field, RootModel, create_model

## This api is experimental and subject to change!

# ================================================================================
# Create custom messages for this platform
class StartPayload(BaseModel):
    payload_type: Literal["Start"] = "Start"

class StopPayload(BaseModel):
    payload_type: Literal["Stop"] = "Stop"

# ================================================================================
# Register payloads into a protocol
class RegisteredPayload(RootModel):
    root: Annotated[
        Union[StartPayload, StopPayload,  LogPayload, HeartbeatPayload],
        Field(discriminator="payload_type", json_schema_extra={"x-abstract": True}),
    ]


RegisteredMessages = create_model(
    "RegisteredMessages",
    __base__=_Message[RegisteredPayload],
)


class Message(RootModel):
    root: _Message[Any]


class MessageProtocol(BaseModel):
    """
    Container for the complete message protocol including all registered message types.

    """

    model_config = ConfigDict(json_schema_extra={"x-abstract": True})
    registered_message: RegisteredMessages
    message: Message