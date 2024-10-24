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
    PRINT_TEXTURE = auto()
    PRINT_PREVIEW_IMAGE = auto()
    PRINT_PREVIEW_NODE_DRAW = auto()
    PRINT_PREVIEW_TITLE_NODE_DRAW = auto()
    PRINT_PREVIEW_SUBTITLE_NODE_DRAW = auto()
    PEN_CONFIG = auto()
    PRINT_BUTTON = auto()
    PEN_REPLACE_MODAL = auto()
