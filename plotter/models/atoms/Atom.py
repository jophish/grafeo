from ...pens import Pen
from ..Bounded import Bounded
from typing import TypedDict, Unpack


class _AtomKwargs(TypedDict):
    pen: Pen


class Atom(Bounded):
    """
    An Atom is a basic element that can appear in a scene.

    This class is intended to be used as a mixin.

    :ivar pen: The pen associated with this atom
    :vartype pen: :class:`Pen`
    """

    def __init__(self, *args, **kwargs: Unpack[_AtomKwargs]):
        """
        Initialize an atom.

        :param pen: A pen identifier
        :type points: class:`plotter.pens.Pen`
        """
        super().__init__(*args, **kwargs)
        self.pen: Pen = kwargs['pen']
