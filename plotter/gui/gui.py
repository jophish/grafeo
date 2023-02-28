import dearpygui.dearpygui as dpg
from math import sin
dpg.create_context()


with dpg.theme() as borderless_child_theme:
    with dpg.theme_component(dpg.mvChildWindow):
        dpg.add_theme_color(dpg.mvThemeCol_Border, [0, 0, 0, 0])

with dpg.window(tag="Tutorial"):
    with dpg.group(horizontal=True):
        # Left pane
        with dpg.child_window(width=300, autosize_y=True):
            dpg.bind_item_theme(dpg.last_item(), borderless_child_theme)
            with dpg.collapsing_header(label='generators'):
                # List all available generators, allow a user to pick one
                dpg.add_button(label='test')
            with dpg.collapsing_header(label='parameters'):
                # Allow user to choose parameters and generate
                dpg.add_button(label='test')
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


dpg.create_viewport(title='Custom Title')
dpg.set_primary_window("Tutorial", True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
