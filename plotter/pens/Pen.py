from enum import IntEnum, auto


class Pen(IntEnum):
    """
    The Pen class is used to differentiate pens within atoms.

    Pens do not have any styling information attached to them; they are simply unique identifiers.
    Styling information is determined at the :class`plotter.models.Model` level, by mapping
    Pen values to styles.
    """

    ONE = auto()
    TWO = auto()
    THREE = auto()
    FOUR = auto()
    FIVE = auto()
    SIX = auto()
    SEVEN = auto()
    EIGHT = auto()
