from abc import ABC, abstractmethod
from typing import Any


class Serializer(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def serialize_command(self, command: Any):
        """
        Serializes a command and sends it to the printer.
        """
        pass
