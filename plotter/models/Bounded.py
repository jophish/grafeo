from abc import ABC, abstractmethod

from .BoundingBox import BoundingBox


class Bounded(ABC):
    """
    Bounded encapsulates the notion of an object that is bounded in two dimensions.

    This class is intended to be used as a mixin.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        pass

    @abstractmethod
    def get_bounding_box(self) -> BoundingBox:
        """
        Get the bounding box of the object.

        :return: Bounding box of the object
        """
        pass
