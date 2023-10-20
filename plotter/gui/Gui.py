import dearpygui.dearpygui as dpg
import math

from plotter.config import ConfigManager
from plotter.generators import GeneratorManager, GeneratorParam, GeneratorParamGroup
from plotter.generators.Parameters import EnumParam, FloatParam, IntParam
from plotter.gui.Tags import Tags
from plotter.renderer import Renderer

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
        self.renderer = Renderer(None, None)
        self.should_render = False

    def _update_render(self):
        model = self.generator_manager.current_generator.model
        bounding_box = model.get_bounding_box()

        canvas_width = bounding_box.max_x - bounding_box.min_x
        canvas_height = bounding_box.max_y - bounding_box.min_y
        window_width, window_height = dpg.get_item_rect_size(Tags.WINDOW)

        max_render_width = window_width - LEFT_PANEL_WIDTH - 50
        max_render_height = window_height - 50

        scale = min(
            1, max_render_width / canvas_width, max_render_height / canvas_height
        )

        render_data = self.renderer.render_data

        if dpg.does_item_exist(Tags.OUTPUT_IMAGE):
            dpg.delete_item(Tags.OUTPUT_IMAGE)
        if dpg.does_item_exist(Tags.PRINT_PREVIEW_IMAGE):
            dpg.delete_item(Tags.PRINT_PREVIEW_IMAGE)
        if dpg.does_item_exist(Tags.TEXTURE):
            dpg.delete_item(Tags.TEXTURE)

        with dpg.texture_registry(show=False):
            dpg.add_dynamic_texture(
                render_data["width"],
                render_data["height"],
                default_value=render_data["data"],
                tag=Tags.TEXTURE,
            )
        dpg.add_image(
            Tags.TEXTURE,
            width=canvas_width * scale,
            height=canvas_height * scale,
            parent=Tags.OUTPUT_PANEL,
            tag=Tags.OUTPUT_IMAGE,
        )

        self._render_print_preview()

        dpg.configure_item(Tags.RENDER_BUTTON, enabled=True)

    def _render_print_preview(self):
        print_settings = self.config_manager.get_print_settings()
        canvas_width = print_settings["max_x_coord"]
        canvas_height = print_settings["max_y_coord"]
        window_width, window_height = dpg.get_item_rect_size(Tags.WINDOW)
        max_render_width = window_width - LEFT_PANEL_WIDTH - 50
        max_render_height = window_height - 50

        draw_width, draw_height = self._scale_to_fit(
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

        render_data = self.renderer.render_data

        img_width, img_height = self._scale_to_fit(
            render_data["width"],
            render_data["height"],
            draw_width - (margin_x_px * 2),
            draw_height - (margin_y_px * 2),
        )

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
                pen_map = self.config_manager.get_pen_map(self.config_manager.get_current_generator(), model.get_used_pens())
                with dpg.draw_node(tag=Tags.PRINT_PREVIEW_NODE_DRAW):
                    for line in model.lines:
                        pen_config = pen_map[str(line.pen.value)]
                        r,g,b,a = bytes.fromhex(pen_config['color'][1:])
                        dpg.draw_polyline(
                            [(point.x, point.y) for point in line.points],
                            color=(r,g,b,a),
                            thickness=pen_config['weight']
                        )


            self._apply_print_preview_transforms()

    def _apply_print_preview_transforms(self):
        if not dpg.does_item_exist(Tags.PRINT_PREVIEW_NODE_DRAW):
            return

        print_settings = self.config_manager.get_print_settings()
        render_data = self.renderer.render_data

        canvas_width = print_settings["max_x_coord"]
        canvas_height = print_settings["max_y_coord"]
        window_width, window_height = dpg.get_item_rect_size(Tags.WINDOW)
        max_render_width = window_width - LEFT_PANEL_WIDTH - 50
        max_render_height = window_height - 50

        margin_x = print_settings["margin_x"]
        margin_y = print_settings["margin_y"]
        frac_marg_x = margin_x / canvas_width
        frac_marg_y = margin_y / canvas_height

        draw_width, draw_height = self._scale_to_fit(
            canvas_width, canvas_height, max_render_width, max_render_height
        )
        margin_x_px = frac_marg_x * draw_width
        margin_y_px = frac_marg_y * draw_height

        render_data = self.renderer.render_data

        img_width, img_height = self._scale_to_fit(
            render_data["width"],
            render_data["height"],
            draw_width - (margin_x_px * 2),
            draw_height - (margin_y_px * 2),
        )

        model = self.generator_manager.current_generator.model
        bounding_box = model.get_bounding_box()

        bounding_box_center_x = (bounding_box.max_x + bounding_box.min_x)/2
        bounding_box_center_y = (bounding_box.max_y + bounding_box.min_y)/2
        # First, translate the model to be centered about the origin
        origin_translate_matrix = dpg.create_translation_matrix((-bounding_box_center_x, -bounding_box_center_y))
        print(origin_translate_matrix)
        print(type(origin_translate_matrix))
        # Since the drawing initially has the size of the model's bounding box, scale it to fit within
        # the margins. We also take into account user-defined scaling here.
        (scaled_x, scaled_y) = self._scale_to_fit(bounding_box.max_x - bounding_box.min_x, bounding_box.max_y - bounding_box.min_y, draw_width - margin_x_px*2, draw_height - margin_y_px*2)
        init_scale = scaled_x/(bounding_box.max_x - bounding_box.min_x)
        print_scale = print_settings["scale"]
        init_scale_matrix = dpg.create_scale_matrix((init_scale*print_scale, init_scale*print_scale, 0))

        # First, translate about z-axis
        rot_matrix = dpg.create_rotation_matrix(math.pi*print_settings['rotation']/180.0, [0, 0, -1])
        # Then, translate into place
        translate_matrix = dpg.create_translation_matrix((draw_width/2, draw_height/2))

        dpg.apply_transform(Tags.PRINT_PREVIEW_NODE_DRAW, translate_matrix*rot_matrix*init_scale_matrix*origin_translate_matrix)

    def _scale_to_fit(
        self, original_x: float, original_y: float, bound_x: float, bound_y: float
    ) -> tuple[float, float]:
        """
        Given a bounding box and some dimensions, scale down/up the dimensions
        such that they fit (maximally) within the bounding box.
        """
        scale = min(1, bound_x / original_x, bound_y / original_y)
        scaled_x = original_x * scale
        scaled_y = original_y * scale
        scale_up = min(bound_x / scaled_x, bound_y / scaled_y)
        return (scaled_x * scale_up, scaled_y * scale_up)

    @_wrap_callback
    def _resize_window_callback(self, app_data, user_data):
        if not dpg.does_item_exist(Tags.OUTPUT_IMAGE):
            return

        model = self.generator_manager.current_generator.model
        bounding_box = model.get_bounding_box()
        canvas_width = bounding_box.max_x - bounding_box.min_x
        canvas_height = bounding_box.max_y - bounding_box.min_y
        window_width, window_height = dpg.get_item_rect_size(Tags.WINDOW)
        max_render_width = window_width - LEFT_PANEL_WIDTH - 50
        max_render_height = window_height - 50
        scale = min(
            1, max_render_width / canvas_width, max_render_height / canvas_height
        )

        dpg.configure_item(
            Tags.OUTPUT_IMAGE, width=canvas_width * scale, height=canvas_height * scale
        )
        self._render_print_preview()

    @_wrap_callback
    def _render_callback(self, app_data, user_data):
        try:
            dpg.configure_item(Tags.RENDER_BUTTON, enabled=False)
            model = self.generator_manager.generate_current()
            self.renderer.render(model)
            self._make_pen_config_section()
            self.should_render = True
        except Exception as e:
            print(f"Error while rendering: {e}")
            dpg.configure_item(Tags.RENDER_BUTTON, enabled=True)
            self.should_render = False

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
    def _update_print_scale_callback(self, param_value, param_name):
        self.config_manager.update_print_setting("scale", param_value)
        self._apply_print_preview_transforms()

    @_wrap_callback
    def _update_print_rotation_callback(self, param_value, param_name):
        self.config_manager.update_print_setting("rotation", param_value)
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
        self.config_manager.update_pen_map(self.config_manager.get_current_generator(), pen, index)
        self._render_print_preview()

    def _make_pen_config_section(self):
        dpg.delete_item(Tags.PEN_CONFIG, children_only=True)
        if not self.generator_manager.current_generator.model:
            return

        used_pens = self.generator_manager.current_generator.model.get_used_pens()
        pen_map = self.config_manager.get_pen_map(self.config_manager.get_current_generator(), used_pens)
        available_pen_configs = self.config_manager.get_available_pen_configs()

        with dpg.table(
            header_row=False,
            borders_outerH=True,
            borders_innerV=False,
            borders_innerH=True,
            borders_outerV=False,
            parent=Tags.PEN_CONFIG
        ):
            dpg.add_table_column()
            for pen, pen_config in pen_map.items():
                with dpg.table_row():
                    with dpg.table_cell():
                        dpg.add_text(default_value=f'Pen {pen}', color=(204, 36, 29))
                        dpg.add_combo(
                            items=[config['descr'] for config in available_pen_configs],
                            user_data=pen,
                            callback=self._update_pen_config,
                            default_value=pen_config['descr']
                        )

    def start(self):
        """Start the GUI."""
        dpg.create_context()
        dpg.create_viewport(title="Custom Title")
        dpg.setup_dearpygui()
        dpg.set_global_font_scale(1)
        with dpg.window(tag=Tags.WINDOW):
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
                    with dpg.collapsing_header(label="print layout"):
                        # Options relating to print layout
                        # paper dimensions: (max x/y GPGL coords)
                        default_print_settings = (
                            self.config_manager.get_print_settings()
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
                                    dpg.add_text(
                                        default_value="scale", color=(204, 36, 29)
                                    )
                                    dpg.add_slider_float(
                                        user_data="scale",
                                        callback=self._update_print_scale_callback,
                                        min_value=0,
                                        max_value=5,
                                        default_value=default_print_settings["scale"],
                                    )
                            with dpg.table_row():
                                with dpg.table_cell():
                                    dpg.add_text(
                                        default_value="rotation", color=(204, 36, 29)
                                    )
                                    dpg.add_slider_float(
                                        user_data="rotation",
                                        callback=self._update_print_rotation_callback,
                                        min_value=0,
                                        max_value=360,
                                        default_value=default_print_settings[
                                            "rotation"
                                        ],
                                    )
                        # rotation
                        # scaling
                        # translation should be handled by dragging on the print preview
                        # pen mapping (map distinct pens in drawing to configured pens)
                        dpg.add_button(label="test")
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
                        with dpg.tab(label="output", tag=Tags.OUTPUT_PANEL):
                            pass
                        with dpg.tab(label="print preview", tag=Tags.PRINT_PREVIEW):
                            pass

                # Right Pane
                with dpg.group():
                    pass

        self._setup_theme()

        with dpg.item_handler_registry(tag=Tags.WINDOW_HANDLER):
            dpg.add_item_resize_handler(callback=self._resize_window_callback)
        dpg.bind_item_handler_registry(Tags.WINDOW, Tags.WINDOW_HANDLER)

        dpg.set_primary_window(Tags.WINDOW, True)
        dpg.show_viewport()
        while dpg.is_dearpygui_running():
            if self.should_render:
                self._update_render()
                self.should_render = False
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
