docstring reference:
https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html

Ideas:

MP4100 (and GPGL in general) supports a variety of builtins that result in higher quality prints than by only using primitive DRAW commands.

In particular, these are:

* DRAW
* CIRCLE
* CURVE
* ELLIPSE

Of these, CURVE seems the most important to implement.

More specifically, we want to generate precedural images for the plotter to print. These images will consist of straight lines, and curves. (Generally, just curves.)
We should represent these generated images as SVGs for ease of displaying/modifying/etc. SVGs define curves as cubic bezier curves; the CURVE command of the plotter draws
cubic splines. A conversion must happen somewhere along the line.

In general, I think we want something like:

* Pick generation parameters
* Generate internal representation (in memory) of generated image
  * eg, data member/class instance per line/curve, etc. etc.
  * Able to serialize and save
* Convert internal rep. into SVG for viewing
  * Able to save
* Convert internal rep. into list of GPGL commands
  * Able to save
* Be able to run program


Issues:

* Handshaking (software XON/XOFF) doesn't work atm
* Read commands don't seem to work
* Exact alignment of plotter is still a mystery/registration with paper
