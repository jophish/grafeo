# grafeo

**N.B. this is a work in progress!!**

**grafeo** is an opinionated, Python-based GUI framework for creating generative & procedural art intended for printing on standard pen plotters.

Grafeo provides a convenient framework for quickly iterating on procedural art generation, allowing users to define parameterized *generators* which output *models* of 2D scenes in response to the selected parameter values. Grafeo renders these 2D scenes, and allows the user to quickly adjust the selected generator's parameter values and re-render the scene. When a desired composition is found, the scene can easily be printed on a connected plotter.

![grafeo user interface](https://github.com/jophish/grafeo/blob/main/assets/grafeo.png?raw=true)

## Features

* Extensible framework for creating parameterized art "generators"
* Extensible printer & serialization support
  * Support for compiling models to GPGL
* Built-in hatching support for arbitrary polygons
* First-class support for multiple pens
* Built-in SVG font rendering
  * First-class support for title/subtitling
* SVG import/rendering
* Support for printing multi-frame SVGs as animation frames

## Structure

Grafeo is split into two separate modes of operation, **generator mode**, for creating and printing procedurally generated scenes, and **svg mode**, for importing and printing SVGs, with animation support.

### Generator Mode
The overall structure of grafeo is relatively simple. Users define `Generator` classes, which accept a number of `Parameter` objects of different types (enum, int, float, bool, etc.). Available generators are automatically added as options in the GUI. When a generator is selected in the
GUI, its available parameters appear and are able to be edited by the user. At any time, you can re-render the model with the current parameters by selecting the **render** button.

Generator classes contain a single method `_generate` which is called on each render. `_generate` is called with a single argument, a dictionary containing the current parameter values of the generator. This is the core method where scene generation occurs. The `_generate` method of each generator is expected to return a `Model` object representing the scene.

At their core, `Model` objects are simply collections of primitive `Line` and `Point` objects, or recursively, other `Model` objects. In addition to requiring coordinate data, `Line` and `Point` objects require a `Pen` to be set. Inherently, no semantics are associated with each pen. At the rendering step, however, grafeo collects data about all pens used by the current model, and allows the user to set a mapping between distinct pens used in the model, and a globally defined collection of actual, physical pens, with distinct properties.

Grafeo has first-class support for overlaying title and subtitle on each work, through a built-in SVG font renderer. See below for instructions on adding support for a new font.

### SVG Mode

SVG mode is grafeo's second mode of operation, with support for importing and printing SVG files (currently only multi-frame). Since many tools for printing SVG files already exist (most obviously, Inkscape), the primary purpose of this mode is for rendering multi-frame SVGs into animation frames with registration marks for ease of printing.

![3D animation printed using a pen plotter](https://github.com/jophish/grafeo/blob/main/assets/out.gif?raw=true)

*A 24 fps, 247-frame animation plotted using grafeo, scanned, and digitally registered & reconstructed.*


![grafeo's SVG mode](https://github.com/jophish/grafeo/blob/main/assets/svg-mode.png?raw=true)

*A multi-frame SVG imported into grafeo's SVG mode, with multiple frames & registration marks per plotted page.*

After entering SVG mode, you can load `./assets/cloth-animation.svg`, which contains a stylized SVG rendering of a cloth falling over a spinning sphere, animated in Blender. In order to print multiple frames per page, you can adjust the number of rows/columns in the side bar, as well as change the size of the registration marks. Pressing the *print* button under the i/o section will print the currently selected page.

Video reconstruction is currently an ad-hoc process, using one-off OpenCV-based scripts to perform computer vision tasks to align registration marks in the scanned frames. In the future, more information will be embedded into the registragion marks/frame margins, such that video reconstruction can be fully automated.

## Adding Fonts

The process for adding a new font is relatively straightforward, however is mostly suited to my own workflows at the moment. If you have a suggestion to automate more of this process, open a PR!

* Ensure `fontforge` is installed and available on your `PATH`.
* First, find a .ttf (TrueType) font file for the font you'd like to add.
* Run `./scripts/convert-font.pe <PATH_TO_.TTF_FILE>`
  * This will convert your TrueType font into an SVG font file.
* Open the generated SVG font file in `fontforge`.
  * Select all glyphs (Ctrl-A), and then run `Element -> Overlap -> Remove Overlap`.
  * Save the SVG font.
  * This simplifies the glyph geometries, and guarantees geometry constraints such that we are always able to correctly determine holes in glyphs via graph algorithms for proper hatching.
* Move the SVG font file into the `./plotter/fonts/svg/` directory. It will automatically be detected by grafeo and made available for use.

At time of writing, there is no special support for kerning. The converted SVG fonts typically specify either a global or per-glyph `horiz-adv-x` attribute which seems to roughly serve as an x-offset to use between glyphs, which is what grafeo currently uses to determine spacing. This means that monospaced typefaces are currently best suited to use.

## TODO

* Import/export model/parameters
* Export as SVG
* Better SVG importing/animation support
  * Implement a proper, orientation-aware registration system for animation frames, with machine-readable metadata in frame margins for automatic reconstruction.
  * Incorporate animation reconstruction directly into GUI.
* Genericize printer/serialization interfaces
* Make app actually usable while printing is happening
