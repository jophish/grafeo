import dearpygui.dearpygui as dpg
from plotter.generators.GeneratorManager import GeneratorManager
from plotter.config.ConfigManager import ConfigManager

# On startup:
# - Initialize config
#   - If no config file is found, create a config file at CONFIG_PATH with default values.
#   - Config includes:
#     - per-generator parameter values
#     - per-generator pen mappings
#     - per-generator print layout
#     - serial port options
#     - Pen configs (available pens)
#     - Current generator selected
# - Fetch saved file paths to populate "files" section
# - Initialize the generator based off of the current config setup, load with saved params
# - Render

# What needs access to the config?
# Generators do not need direct access, but the GeneratorManager does.
# ConfigManager needs access to GeneratorManager, to get default configs
# for each Generator

LEFT_PANEL_WIDTH = 600
LEFT_PANEL_MARGIN = 30
LEFT_PANEL_TEXT_WRAP = LEFT_PANEL_WIDTH - LEFT_PANEL_MARGIN

def select_generator_callback(sender, app_data, user_data):
    user_data['generator_manager'].set_current_generator_by_friendly_name(app_data)
    generator_name = user_data['generator_manager'].get_name_by_friendly_name(app_data)
    user_data['config_manager'].set_current_generator(generator_name)
    dpg.delete_item('parameters', children_only=True)
    make_parameter_items(user_data)

def update_parameter_callback(sender, app_data, user_data):
    param_name = user_data['param_name']
    managers = user_data['managers']
    managers['config_manager'].set_param_value(param_name, app_data)
    managers['generator_manager'].current_generator.set_param_value(param_name, app_data)

def make_parameter_items(managers):
    current_generator = managers['generator_manager'].current_generator
    param_list = current_generator.get_param_list()
    with dpg.table(
            header_row=False, parent='parameters',
            borders_outerH=True, borders_innerV=False, borders_innerH=True, borders_outerV=False
    ):

        dpg.add_table_column()

        for (param_name, param_details) in param_list.items():
            with dpg.table_row():
                with dpg.table_cell():
                    user_data = {
                        'param_name': param_name,
                        'managers': managers
                    }
                    current_param_value = managers['generator_manager'].get_current_generator_param_value(param_name)
                    dpg.add_text(
                        default_value=param_name,
                        color=(204, 36, 29)
                    )
                    dpg.add_text(
                        default_value=param_details[1],
                        wrap=LEFT_PANEL_TEXT_WRAP
                    )
                    if param_details[2] == 'int':
                        dpg.add_slider_int(
                            user_data=user_data,
                            callback=update_parameter_callback,
                            min_value=param_details[3],
                            max_value=param_details[4],
                            default_value=current_param_value
                        )
                    elif param_details[2] == 'float':
                        dpg.add_slider_float(
                            user_data=user_data,
                            callback=update_parameter_callback,
                            min_value=param_details[3],
                            max_value=param_details[4],
                            default_value=current_param_value
                        )
                    elif param_details[2] == 'enum':
                        dpg.add_combo(
                            items=param_details[3],
                            user_data=user_data,
                            callback=update_parameter_callback,
                            default_value=current_param_value
                        )


def setup_gui(managers):
    dpg.create_context()
    dpg.set_global_font_scale(2)
    with dpg.theme() as borderless_child_theme:
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_Border, [0, 0, 0, 0])

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (29, 32, 33), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (29, 32, 33), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (29, 32, 33), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Header, (102, 92, 84), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (69, 133, 136), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (69, 133, 136), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (131, 165, 152), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (131, 165, 152), category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
        with dpg.theme_component(dpg.mvInputInt):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (140, 255, 23), category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)

    with dpg.window(tag="Tutorial"):
        with dpg.group(horizontal=True):
            # Left pane
            with dpg.child_window(width=LEFT_PANEL_WIDTH, autosize_y=True):
                dpg.bind_item_theme(dpg.last_item(), borderless_child_theme)
                with dpg.collapsing_header(label='generators'):
                    # List all available generators, allow a user to pick one
                    dpg.add_radio_button(
                        label='generator',
                        items=managers['generator_manager'].get_generator_friendly_names(),
                        default_value=managers['generator_manager'].current_generator.get_friendly_name(),
                        user_data=managers,
                        callback=select_generator_callback
                    )
                with dpg.collapsing_header(label='parameters', tag='parameters'):
                    # Allow user to choose parameters and generate
                    make_parameter_items(managers)
                with dpg.collapsing_header(label='i/o'):
                    # Set Serial port options
                    dpg.add_button(label='test')
                with dpg.collapsing_header(label='print layout'):
                    # Options relating to print layout
                    # paper dimensions: (max x/y GPGL coords)
                    # rotation
                    # scaling
                    # translation should be handled by dragging on the print preview
                    # pen mapping (map distinct pens in drawing to configured pens)
                    dpg.add_button(label='test')
                with dpg.collapsing_header(label='pens'):
                    # Add/Remove/Edit available pens
                    dpg.add_button(label='test')
                with dpg.collapsing_header(label='files'):
                    # Load/Save files/presets
                    dpg.add_button(label='test')
                with dpg.group(horizontal=True):
                    dpg.add_button(label='save')
                    dpg.add_input_text(label='filaname', default_value='filename.plt')

            # Middle Pane
            with dpg.group():
                pass
            # Right Pane
            with dpg.group():
                pass
            # Bottom Pane
        with dpg.group(horizontal=True):
            with dpg.collapsing_header(label='test'):
                dpg.add_button(label='test')

    dpg.bind_theme(global_theme)
    dpg.create_viewport(title='Custom Title')
    dpg.set_primary_window("Tutorial", True)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

