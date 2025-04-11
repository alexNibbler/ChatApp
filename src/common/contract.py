from dataclasses import dataclass
from enum import Enum
import typing as ty
import pickle


class Action(Enum):
    CONNECT = 1
    INDIRECT_MESSAGE = 2
    DIRECT_MESSAGE = 3
    GET_ADDRESS = 4
    DIRECT_SEND_FILE = 5


class Message:
    def __init__(self,
                 action: Action,
                 from_username: str,
                 text: str | None = None,
                 file_bytes: bytes | None = None):
        self.action = action
        self.from_username = from_username
        self.text = text
        self.file_bytes = file_bytes

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    @classmethod
    def deserialize(cls, msg_bytes) -> ty.Self:
        return pickle.loads(msg_bytes)


