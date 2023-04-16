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



Pen config:

- If no model exists, do not render section
- When a model is generated, if section is not rendered, render section.
  - There may a stored pen mapping in the config for this model. If there is:
	- For each pen in the stored mapping that's also used in the model, render it as an option with the saved default
	- If a pen is missing from the config but appears in the model, render the section and use the default pen, and write
		this new pen to the model's config
  - If there is not a stored pen mapping in the config:
	- Write config for each pen in the modeln, with the default pen selected
- If the section is rendered, re-render with the same pen semantics as above.


# Printin

High level

- For each pen used in the model, generate a chunk of GPGL


Total GPGL generation:
 Given:
   - Model
   - Scale
   - Rotation
   - Print parameters (max_x, max_y)
 Return:
 A list of objects.

 Each object has two entires, "gpgl" and "precondition".
 "gpgl" is a list of GPGL commands (which are just strings).
 "precondition" is a human-readable string that represents some action the user must take before
 the GPGL in "gpgl" is executed. This will be displayed to the user in a modal and require them to acknowledge
 (handled higher up in the callstack)

GPGL generation:
 Given:
	- List of lines
	- Scale
	- Rotation
	- Print parameters (max_x, max_y) of GPGL

- Generate transformation matrix "mat" from "model space" -> "GPGL space"
- Pick up pen
- For each line:
  - get first point, move to mat*pt (Mxy)
  - for each subsequent point Dxy
- Set pen down

