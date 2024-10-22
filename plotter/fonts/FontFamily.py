from abc import ABC, abstractmethod
from plotter.models.Model import Model

class FontFamily(ABC):

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_glyph_model(self, glyph_name) -> "Model":
        pass

    @abstractmethod
    def get_text_model(self, lines) -> "Model":
        """
        Generate a model representing lines of text.

        Text is left-justified.
        """
        pass
