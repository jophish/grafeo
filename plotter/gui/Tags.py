from enum import StrEnum, auto


class Tags(StrEnum):
    """Enum for dpg tags."""

    WINDOW = auto()
    WINDOW_HANDLER = auto()
    PARAMETERS = auto()
    TEXTURE = auto()
    OUTPUT_PANEL = auto()
    OUTPUT_IMAGE = auto()
    RENDER_BUTTON = auto()
    PRINT_PREVIEW = auto()
    PRINT_PREVIEW_IMAGE = auto()
