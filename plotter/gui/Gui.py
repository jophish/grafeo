import math
import traceback

import dearpygui.dearpygui as dpg

from plotter.config import ConfigManager
from plotter.fonts.FontManager import FontManager
from plotter.generators import (GeneratorManager, GeneratorParam,
                                GeneratorParamGroup)
from plotter.generators.Parameters import EnumParam, FloatParam, IntParam
from plotter.gui.Tags import Tags
from plotter.printers.SerialPrinter import SerialPrinter
from plotter.utils.scaling import scale_to_fit

LEFT_PANEL_WIDTH = 400
LEFT_PANEL_MARGIN = 30
LEFT_PANEL_TEXT_WRAP = LEFT_PANEL_WIDTH - LEFT_PANEL_MARGIN
MIN_VIEWPORT_WIDTH = 1000
MIN_VIEWPORT_HEIGHT = 1000


def _wrap_callback(cb):
    def wrapped(sender, tag, app_data, user_data):
        cb(sender, app_data, user_data)

    return wrapped


class Gui:
    """Primary class to manage the GUI."""

    def __init__(self):
        """Initialize the GUI."""
        # Initialize all available generators using their defaults
        self.generator_manager = GeneratorManager()
        # Sync config with disk
        self.config_manager = ConfigManager(
            self.generator_manager.get_generator_defaults()
        )
        # Load generator configs from disk
        self.generator_manager.set_all_generator_param_values(
            self.config_manager.get_all_generator_param_values()
        )
        # Set current generator from disk
        self.generator_manager.set_current_generator(
            self.config_manager.get_current_generator()
        )
        self.printer = SerialPrinter(self.config_manager.get_serial_settings())

        self.font_manager = FontManager()

        self.title = None
        self.subtitle = None

        self.modal_visible = False

    def _render_print_preview(self):
        print_settings = self.config_manager.get_print_settings()
        canvas_width = print_settings["max_x_coord"]
        canvas_height = print_settings["max_y_coord"]
        window_width, window_height = dpg.get_item_rect_size(Tags.WINDOW)
        max_render_width = window_width - LEFT_PANEL_WIDTH - 50
        max_render_height = window_height - 50

        draw_width, draw_height = scale_to_fit(
            canvas_width, canvas_height, max_render_width, max_render_height
        )

        if dpg.does_item_exist(Tags.PRINT_PREVIEW_IMAGE):
            dpg.delete_item(Tags.PRINT_PREVIEW_IMAGE)

        margin_x = print_settings["margin_x"]
        margin_y = print_settings["margin_y"]
        frac_marg_x = margin_x / canvas_width
        frac_marg_y = margin_y / canvas_height

        margin_x_px = frac_marg_x * draw_width
        margin_y_px = frac_marg_y * draw_height

        with dpg.drawlist(
            parent=Tags.PRINT_PREVIEW,
            width=draw_width,
            height=draw_height,
            tag=Tags.PRINT_PREVIEW_IMAGE,
        ):
            with dpg.draw_layer():
                dpg.draw_polygon(
                    points=[
                        [0, 0],
                        [draw_width, 0],
                        [draw_width, draw_height],
                        [0, draw_height],
                    ],
                    fill=[255, 255, 255],
                    color=[255, 255, 255],
                )
            with dpg.draw_layer():
                # Draw margins
                dpg.draw_line(
                    [margin_x_px, margin_y_px],
                    [draw_width - margin_x_px, margin_y_px],
                    color=(150, 0, 0),
                )
                dpg.draw_line(
                    [draw_width - margin_x_px, margin_y_px],
                    [draw_width - margin_x_px, draw_height - margin_y_px],
                    color=(150, 0, 0),
                )
                dpg.draw_line(
                    [draw_width - margin_x_px, draw_height - margin_y_px],
                    [margin_x_px, draw_height - margin_y_px],
                    color=(150, 0, 0),
                )
                dpg.draw_line(
                    [margin_x_px, draw_height - margin_y_px],
                    [margin_x_px, margin_y_px],
                    color=(150, 0, 0),
                )
            with dpg.draw_layer():
                model = self.generator_manager.current_generator.model
                pen_map = self.config_manager.get_pen_map(
                    self.config_manager.get_current_generator(), model.get_used_pens()
                )
                with dpg.draw_node(tag=Tags.PRINT_PREVIEW_NODE_DRAW):
                    for line in model.all_lines:
                        pen_config = pen_map[str(line.pen.value)]
                        r, g, b, a = bytes.fromhex(pen_config["color"][1:])
                        dpg.draw_polyline(
                            [(point.x, point.y) for point in line.points],
                            color=(r, g, b, a),
                            thickness=pen_config["weight"],
                        )

            self._apply_print_preview_transforms(
                Tags.PRINT_PREVIEW_NODE_DRAW,
                self.generator_manager.current_generator.model,
            )

    def _apply_print_preview_transforms(
            self,
            tag,
            model,
            translate_x,
            translate_y
    ):
        """
        :param tag: Tag to apply transforms to
        :param model: Model associated with the given tag
        """
        if not dpg.does_item_exist(tag):
            return

        print_settings = self.config_manager.get_print_settings()

        canvas_width = print_settings["max_x_coord"]
        canvas_height = print_settings["max_y_coord"]
        window_width, window_height = dpg.get_item_rect_size(Tags.WINDOW)
        max_render_width = window_width - LEFT_PANEL_WIDTH - 50
        max_render_height = window_height - 50

        margin_x = print_settings["margin_x"]
        margin_y = print_settings["margin_y"]
        frac_marg_x = margin_x / canvas_width
        frac_marg_y = margin_y / canvas_height

        draw_width, draw_height = scale_to_fit(
            canvas_width, canvas_height, max_render_width, max_render_height
        )
        margin_x_px = frac_marg_x * draw_width
        margin_y_px = frac_marg_y * draw_height

        bounding_box = model.get_bounding_box()
        width = bounding_box.max_x - bounding_box.min_x
        height = bounding_box.max_y - bounding_box.min_y

        img_width, img_height = scale_to_fit(
            width,
            height,
            draw_width - (margin_x_px * 2),
            draw_height - (margin_y_px * 2),
        )

        bounding_box_center_x = (bounding_box.max_x + bounding_box.min_x) / 2
        bounding_box_center_y = (bounding_box.max_y + bounding_box.min_y) / 2

        # First, translate the model to be centered about the origin
        origin_translate_matrix = dpg.create_translation_matrix(
            (-bounding_box_center_x, -bounding_box_center_y)
        )

        # Since the drawing initially has the size of the model's bounding box, scale it to fit within
        # the margins. We also take into account user-defined scaling here.
        (scaled_x, scaled_y) = scale_to_fit(
            bounding_box.max_x - bounding_box.min_x,
            bounding_box.max_y - bounding_box.min_y,
            draw_width - margin_x_px * 2,
            draw_height - margin_y_px * 2,
        )
        init_scale = scaled_x / (bounding_box.max_x - bounding_box.min_x)
        print_scale = print_settings["scale"]
        # Note the negative y-axis scaling factor. This is necessary, since the coordinate system
        # in dpg has a different origin definition than we do... I think.
        init_scale_matrix = dpg.create_scale_matrix(
            (init_scale * print_scale, -init_scale * print_scale, 0)
        )

        # First, translate about z-axis
        rot_matrix = dpg.create_rotation_matrix(
            math.pi * print_settings["rotation"] / 180.0, [0, 0, -1]
        )

        # Then, translate into place, taking into account additional translations
        scaled_translation_x = (
            print_settings["translate_x"] / print_settings["max_x_coord"] * draw_width
        )
        scaled_translation_y = (
            print_settings["translate_y"] / print_settings["max_y_coord"] * draw_height
        )
        translate_matrix = dpg.create_translation_matrix(
            (
                draw_width / 2 + scaled_translation_x,
                draw_height / 2 + scaled_translation_y,
            )
        )

        dpg.apply_transform(
            tag,
            translate_matrix * rot_matrix * init_scale_matrix * origin_translate_matrix,
        )

    @_wrap_callback
    def _resize_window_callback(self, app_data, user_data):
        self._render_print_preview()

    @_wrap_callback
    def _print_callback(self, app_data, user_data):
        model = self.generator_manager.current_generator.model
        self.printer.begin_print(
            model,
            self.config_manager.get_pen_map(
                self.config_manager.get_current_generator(), model.get_used_pens()
            ),
            self.config_manager.get_print_settings(),
        )
        pass

    @_wrap_callback
    def _render_callback(self, app_data, user_data):
        try:
            dpg.configure_item(Tags.RENDER_BUTTON, enabled=False)
            self.generator_manager.generate_current()
            self._make_pen_config_section()
            self._render_print_preview()
            dpg.configure_item(Tags.RENDER_BUTTON, enabled=True)
        except Exception as e:
            print(f"Error while rendering: {e}")
            print(traceback.format_exc())
            dpg.configure_item(Tags.RENDER_BUTTON, enabled=True)

    @_wrap_callback
    def _select_generator_callback(self, generator_name, user_data):
        self.generator_manager.set_current_generator(generator_name)
        self.config_manager.set_current_generator(generator_name)
        dpg.delete_item(Tags.PARAMETERS, children_only=True)
        self._make_parameter_items()

    @_wrap_callback
    def _update_parameter_callback(self, param_value, param: GeneratorParam):
        param.value = param_value
        self.config_manager.set_generator_params(
            self.generator_manager.current_generator
        )

    @_wrap_callback
    def _update_print_layout_callback(self, param_value, param_name):
        self.config_manager.update_print_setting(param_name, param_value)
        self._apply_print_preview_transforms()

    def _make_parameter_group(self, param_group: GeneratorParamGroup):
        for name, param in param_group.params.items():
            if isinstance(param, GeneratorParamGroup):
                self._make_parameter_group(param)
            elif isinstance(param, GeneratorParam):
                with dpg.table_row():
                    with dpg.table_cell():
                        current_param_value = param.value
                        dpg.add_text(default_value=name, color=(204, 36, 29))
                        dpg.add_text(
                            default_value=param.description, wrap=LEFT_PANEL_TEXT_WRAP
                        )
                        if isinstance(param, IntParam):
                            dpg.add_slider_int(
                                user_data=param,
                                callback=self._update_parameter_callback,
                                min_value=param.min_value,
                                max_value=param.max_value,
                                default_value=current_param_value,
                            )
                        elif isinstance(param, FloatParam):
                            dpg.add_slider_float(
                                user_data=param,
                                callback=self._update_parameter_callback,
                                min_value=param.min_value,
                                max_value=param.max_value,
                                default_value=current_param_value,
                            )
                        elif isinstance(param, EnumParam):
                            dpg.add_combo(
                                items=param.options,
                                user_data=param,
                                callback=self._update_parameter_callback,
                                default_value=current_param_value,
                            )

    def _make_parameter_items(self):
        current_generator = self.generator_manager.current_generator

        dpg.add_button(
            label="render",
            callback=self._render_callback,
            tag=Tags.RENDER_BUTTON,
            parent=Tags.PARAMETERS,
        )

        param_group = current_generator.params

        with dpg.table(
            header_row=False,
            parent=Tags.PARAMETERS,
            borders_outerH=True,
            borders_innerV=False,
            borders_innerH=True,
            borders_outerV=False,
        ):
            dpg.add_table_column()
            self._make_parameter_group(param_group)

    @_wrap_callback
    def _update_pen_config(self, descr, pen):
        index = self.config_manager.get_pen_index_by_desc(descr)
        self.config_manager.update_pen_map(
            self.config_manager.get_current_generator(), pen, index
        )
        self._render_print_preview()

    def _make_pen_config_section(self):
        dpg.delete_item(Tags.PEN_CONFIG, children_only=True)
        if not self.generator_manager.current_generator.model:
            return

        used_pens = self.generator_manager.current_generator.model.get_used_pens()
        pen_map = self.config_manager.get_pen_map(
            self.config_manager.get_current_generator(), used_pens
        )
        available_pen_configs = self.config_manager.get_available_pen_configs()

        with dpg.table(
            header_row=False,
            borders_outerH=True,
            borders_innerV=False,
            borders_innerH=True,
            borders_outerV=False,
            parent=Tags.PEN_CONFIG,
        ):
            dpg.add_table_column()
            for pen, pen_config in pen_map.items():
                with dpg.table_row():
                    with dpg.table_cell():
                        dpg.add_text(default_value=f"Pen {pen}", color=(204, 36, 29))
                        dpg.add_combo(
                            items=[config["descr"] for config in available_pen_configs],
                            user_data=pen,
                            callback=self._update_pen_config,
                            default_value=pen_config["descr"],
                        )

    @_wrap_callback
    def _pen_replaced(self, app_data, user_data):
        dpg.configure_item(Tags.PEN_REPLACE_MODAL, show=False)
        self.modal_visible = False
        self.printer.continue_print()

    def _update_pen_replace_modal(self):
        self.modal_visible = True
        dpg.delete_item(Tags.PEN_REPLACE_MODAL, children_only=True)
        dpg.add_text(
            "Once plotting has paused, please replace pen",
            parent=Tags.PEN_REPLACE_MODAL,
        )
        dpg.add_text(
            "Wait up to 8 seconds for the current pen to be returned to its bay",
            parent=Tags.PEN_REPLACE_MODAL,
        )
        dpg.add_separator(parent=Tags.PEN_REPLACE_MODAL)
        dpg.add_text(
            f'Pen to load: {self.printer.pen_to_replace["descr"]}',
            parent=Tags.PEN_REPLACE_MODAL,
        )
        dpg.add_separator(parent=Tags.PEN_REPLACE_MODAL)

        if self.printer.pen_to_replace.get("load_directly", False):
            dpg.add_text(
                "Load the pen directly into holder. It's okay to move the print head during this process.",
                parent=Tags.PEN_REPLACE_MODAL,
            )
        else:
            dpg.add_text(
                f'Slot to load in: {self.printer.pen_to_replace["location"]}',
                parent=Tags.PEN_REPLACE_MODAL,
            )

        dpg.add_button(
            label="I've replaced the pen",
            callback=self._pen_replaced,
            parent=Tags.PEN_REPLACE_MODAL,
        )

        dpg.configure_item(Tags.PEN_REPLACE_MODAL, show=True)

    def _make_print_settings_section(self):
        # Options relating to print layout
        default_print_settings = self.config_manager.get_print_settings()
        print_settings = self.config_manager.get_print_settings()
        with dpg.table(
            header_row=False,
            borders_outerH=True,
            borders_innerV=False,
            borders_innerH=True,
            borders_outerV=False,
        ):
            dpg.add_table_column()
            with dpg.table_row():
                with dpg.table_cell():
                    dpg.add_text(default_value="scale", color=(204, 36, 29))
                    dpg.add_slider_float(
                        user_data="scale",
                        callback=self._update_print_layout_callback,
                        min_value=0,
                        max_value=5,
                        default_value=default_print_settings["scale"],
                    )
            with dpg.table_row():
                with dpg.table_cell():
                    dpg.add_text(default_value="rotation", color=(204, 36, 29))
                    dpg.add_slider_float(
                        user_data="rotation",
                        callback=self._update_print_layout_callback,
                        min_value=0,
                        max_value=360,
                        default_value=default_print_settings["rotation"],
                    )
            with dpg.table_row():
                with dpg.table_cell():
                    dpg.add_text(default_value="translate_x", color=(204, 36, 29))
                    dpg.add_slider_float(
                        user_data="translate_x",
                        callback=self._update_print_layout_callback,
                        min_value=-print_settings["max_x_coord"] / 2,
                        max_value=print_settings["max_x_coord"] / 2,
                        default_value=default_print_settings["translate_x"],
                    )
                    dpg.add_text(default_value="translate_y", color=(204, 36, 29))
                    dpg.add_slider_float(
                        user_data="translate_y",
                        callback=self._update_print_layout_callback,
                        min_value=-print_settings["max_y_coord"] / 2,
                        max_value=print_settings["max_y_coord"] / 2,
                        default_value=default_print_settings["translate_y"],
                    )

    @_wrap_callback
    def _update_title_callback(self, param_value, param_name):
        self.config_manager.update_title_setting(param_name[0], param_name[1], param_value)
        self._apply_print_preview_transforms()

    def _make_title_settings_section(self):
        # Options relating to print layout
        print_settings = self.config_manager.get_print_settings()
        title_settings = self.config_manager.get_title_settings()
        fonts = self.font_manager.get_fonts()

        def make_section(text_item):
            with dpg.collapsing_header(label=text_item, indent=20):
                dpg.add_text(default_value=f'show {text_item}', color=(204, 36, 29))
                dpg.add_checkbox(
                    user_data=(text_item, "show"),
                    callback=self._update_title_callback,
                    default_value=title_settings[text_item]['show'],
                )
                dpg.add_text(default_value="font", color=(204, 36, 29))
                dpg.add_combo(
                    user_data=("title", "font"),
                    items=fonts,
                    callback=self._update_title_callback,
                    default_value=title_settings[text_item]['font'],
                )
                dpg.add_text(default_value='hatch', color=(204, 36, 29))
                dpg.add_checkbox(
                    user_data=(text_item, "hatch"),
                    callback=self._update_title_callback,
                    default_value=title_settings[text_item]['hatch'],
                )
                dpg.add_text(default_value="hatch angle", color=(204, 36, 29))
                dpg.add_slider_float(
                    user_data=("title", "hatch_angle"),
                    callback=self._update_title_callback,
                    default_value=title_settings[text_item]['hatch_angle'],
                    min_value=-180,
                    max_value=180,
                )
                dpg.add_text(default_value="hatch spacing", color=(204, 36, 29))
                dpg.add_slider_float(
                    user_data=("title", "hatch_spacing"),
                    callback=self._update_title_callback,
                    default_value=title_settings[text_item]['hatch_spacing'],
                    min_value=1,
                    max_value=200,
                )
                dpg.add_text(default_value="height", color=(204, 36, 29))
                dpg.add_slider_float(
                    user_data=("title", "height"),
                    callback=self._update_title_callback,
                    default_value=title_settings[text_item]['height'],
                    min_value=1,
                    max_value=300,
                )
                dpg.add_text(default_value="rotation", color=(204, 36, 29))
                dpg.add_slider_float(
                    user_data=("title", "rotation"),
                    callback=self._update_title_callback,
                    min_value=0,
                    max_value=360,
                    default_value=title_settings[text_item]['rotation'],
                )
                dpg.add_text(default_value="translate_x", color=(204, 36, 29))
                dpg.add_slider_float(
                    user_data=("title", "translate_x"),
                    callback=self._update_title_callback,
                    min_value=-print_settings["max_y_coord"] / 2,
                    max_value=print_settings["max_y_coord"] / 2,
                    default_value=title_settings[text_item]['translate_x'],
                )
                dpg.add_text(default_value="translate_y", color=(204, 36, 29))
                dpg.add_slider_float(
                    user_data=("title", "translate_y"),
                    callback=self._update_title_callback,
                    min_value=-print_settings["max_y_coord"] / 2,
                    max_value=print_settings["max_y_coord"] / 2,
                    default_value=title_settings[text_item]['translate_y'],
                )

        with dpg.table(
            header_row=False,
            borders_outerH=True,
            borders_innerV=False,
            borders_innerH=True,
            borders_outerV=False,
        ):
            dpg.add_table_column()
            with dpg.table_row():
                with dpg.table_cell():
                    for text_item in ["title", "subtitle"]:
                        make_section(text_item)


    def start(self):
        """Start the GUI."""
        dpg.create_context()
        dpg.create_viewport(title="Custom Title")
        dpg.setup_dearpygui()
        dpg.set_global_font_scale(1)
        with dpg.window(tag=Tags.WINDOW):
            # Pop-up to confirm pen replacement
            with dpg.window(
                label="Replace Pen",
                modal=True,
                show=False,
                tag=Tags.PEN_REPLACE_MODAL,
                no_title_bar=True,
            ):
                pass
            with dpg.group(horizontal=True):
                # Left pane
                with dpg.child_window(width=LEFT_PANEL_WIDTH, autosize_y=True):
                    with dpg.collapsing_header(label="generators"):
                        # List all available generators, allow a user to pick one
                        dpg.add_radio_button(
                            label="generator",
                            items=self.generator_manager.get_generator_names(),
                            default_value=self.generator_manager.current_generator.name,
                            callback=self._select_generator_callback,
                        )
                    with dpg.collapsing_header(label="parameters", tag=Tags.PARAMETERS):
                        # Allow user to choose parameters and generate
                        self._make_parameter_items()
                    with dpg.collapsing_header(label="i/o"):
                        # Set Serial port options
                        dpg.add_button(label="test")
                        dpg.add_button(
                            label="print",
                            callback=self._print_callback,
                            tag=Tags.PRINT_BUTTON,
                        )
                    with dpg.collapsing_header(label="print layout"):
                        self._make_print_settings_section()
                    with dpg.collapsing_header(label="title & subtitle"):
                        self._make_title_settings_section()
                    with dpg.collapsing_header(label="pens", tag=Tags.PEN_CONFIG):
                        self._make_pen_config_section()
                    with dpg.collapsing_header(label="files"):
                        # Load/Save files/presets
                        dpg.add_button(label="test")
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="save")
                        dpg.add_input_text(
                            label="filaname", default_value="filename.plt"
                        )

                # Middle Pane
                with dpg.group(tag="middle"):
                    with dpg.tab_bar():
                        with dpg.tab(label="print preview", tag=Tags.PRINT_PREVIEW):
                            pass

                # Right Pane
                with dpg.group():
                    pass

        with dpg.item_handler_registry(tag=Tags.WINDOW_HANDLER):
            dpg.add_item_resize_handler(callback=self._resize_window_callback)
        dpg.bind_item_handler_registry(Tags.WINDOW, Tags.WINDOW_HANDLER)

        dpg.set_primary_window(Tags.WINDOW, True)
        dpg.show_viewport()

        # Update render once on start to show empty canvas
        self.should_render = True
        while dpg.is_dearpygui_running():
            if self.printer.printing_needs_user_input and not self.modal_visible:
                self._update_pen_replace_modal()

            dpg.render_dearpygui_frame()

        dpg.destroy_context()

    def _setup_theme(self):
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(
                    dpg.mvThemeCol_FrameBg, (29, 32, 33), category=dpg.mvThemeCat_Core
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_WindowBg, (29, 32, 33), category=dpg.mvThemeCat_Core
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_ChildBg, (29, 32, 33), category=dpg.mvThemeCat_Core
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_Header, (102, 92, 84), category=dpg.mvThemeCat_Core
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_HeaderHovered,
                    (69, 133, 136),
                    category=dpg.mvThemeCat_Core,
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_ButtonHovered,
                    (69, 133, 136),
                    category=dpg.mvThemeCat_Core,
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_ButtonActive,
                    (131, 165, 152),
                    category=dpg.mvThemeCat_Core,
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_HeaderActive,
                    (131, 165, 152),
                    category=dpg.mvThemeCat_Core,
                )
                dpg.add_theme_style(
                    dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core
                )
            with dpg.theme_component(dpg.mvInputInt):
                dpg.add_theme_color(
                    dpg.mvThemeCol_FrameBg, (140, 255, 23), category=dpg.mvThemeCat_Core
                )
                dpg.add_theme_style(
                    dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core
                )
        dpg.bind_theme(theme)
