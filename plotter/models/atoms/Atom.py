from ...pens.Pen import Pen
from ..Bounded import Bounded


class Atom(Bounded):
    """
    An Atom is a basic element that can appear in a scene.

    This class is intended to be used as a mixin.

    :ivar pen:
    :vartype pen: class:`plotter.pens.Pen`
    """

    pen: Pen

    def __init__(self, *args, **kwargs):
        """
        Initialize an atom.

        :param pen: A pen identifier
        :type points: class:`plotter.pens.Pen`
        """
        super().__init__(*args, **kwargs)
        self.pen = kwargs['pen']
