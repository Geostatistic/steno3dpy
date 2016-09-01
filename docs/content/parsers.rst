.. _parsers:

Parsers
=======

The Steno3D Python client is designed to support developers by providing
an object-oriented, file-type agnostic environment to work with. However,
it contains the infrastructure for parsers as plugin modules to suppport
file-heavy workflows.

- :ref:`using_parsers`
- :ref:`recognized_parsers`
- :ref:`contributing`

.. _using_parsers:

Installing and Using Parsers
----------------------------

An example parser for Wavefront .obj files is available on
`pip <https://pypi.python.org/pypi/steno3d_obj>`_:

.. code::

    pip install steno3d_obj

or install from `source <https://github.com/3ptscience/steno3d-obj>`_:

.. code::

    git clone https://github.com/3ptscience/steno3d-obj.git
    python setup.py install

Usage of all parsers should be the same as the obj parser.
Upon import, the parser is added to the Steno3D namespace and may be
instantiated with the name of the input file.

.. code::

    >> import steno3d
    >> import steno3d_obj
    >> obj_parser = steno3d.parsers.obj('/path/to/input/file.obj')

If you have many different parsers imported, you may also let Steno3D
select the appropriate parser based on file extension using:

.. code::

    >> obj_parser = steno3d.parsers.AllParsers('/path/to/input/file.obj')

Then, to parse the file into a new Steno3D project:

.. code::

    >> (obj_proj,) = obj_parser.parse()

You may also parse the file objects directly into an existing Steno3d project.

.. code::

    >> my_proj = steno3d.Project(
           title='OBJ File Project'
       )
    >> obj_parser.parse(my_proj)

.. _recognized_parsers:

Links to Parsers
-----------------------------

- obj parser for Wavefront .obj files
  (`github <https://github.com/3ptscience/steno3d-obj>`_,
  `pip <https://pypi.python.org/pypi/steno3d_obj>`_)
- stl parser for binary and ASCII stereolithography .stl files
  (`github <https://github.com/3ptscience/steno3d-stl>`_,
  `pip <https://pypi.python.org/pypi/steno3d_stl>`_)


.. _contributing:

Contributing
------------

If there is a 3D file type you would like to see supported or an existing
parser you would like expanded, please contribute! The basic guidelines
for our parsers are

#. Easy to use by following the steps described :ref:`above <using_parsers>`
#. Well-documented coverage of the file type (not necessarily supporting
   every feature, but describing what is supported and raising non-cryptic
   warnings or errors for unsupported features)
#. Open source, under the MIT license if possible
#. `PEP 8 compliant <https://www.python.org/dev/peps/pep-0008/>`_
   (aside from parser class names) and
   `Python 2/3 compatible <http://python-future.org/compatible_idioms.html>`_

Additional details for writing a parser follow :ref:`below <implementation>`.
If you are interested in a new parser parser or have feedback about an
existing parser but are unable to contribute, please at least submit an
issue to
`steno3d <https://github.com/3ptscience/steno3dpy/issues>`_
or the specific parser's github page.

.. _implementation:

Implementation
++++++++++++++

The following steps describe how to implement a Steno3D parser. Please
refer to the `obj parser source code <https://github.com/3ptscience/steno3d-obj>`_
as an example.

Class Definition
****************

Parser classes must inherit :code:`BaseParser` and they must have a tuple
of supported extensions:

.. code::

    ...
    import steno3d


    class obj(steno3d.parsers.BaseParser):
        """class obj

        Parser class for Wavefront .obj ASCII object files
        """

        extensions = ('obj',)
        ...

Doing this adds the parser to the :code:`steno3d.parsers` namespace, adds
the extension to the steno3d supported extensions, and ensures that files
have the appropriate extension.

In this example, the lowercase class names deviates from PEP 8 style.
However, we break this rule to allow for symmetry between class names
and file extensions.

Initialization
**************

Initialization is handled by the :code:`BaseParser` :code:`__init__`
function. The only required parameter is the file name. Therefore,
:code:`self.file_name` is available to any function defined in your parser.
There are two initialization hooks:

.. code::

    def _validate_file(self, file_name):
        """function _validate_file

        Input:
            file_name - The file to be validated

        Output:
            validated file_name

        _validate_file verifies the file exists and the extension matches
        the parser extension(s) before proceeding. This hook can be
        overwritten to perform different file checks or remove the checks
        entirely as long as it returns the file_name.
        """

and

.. code::

    def _initialize(self):
        """function _initialize

        _initialize is a hook that is called during parser __init__
        after _validate_file. It can be overwritten to perform any
        additional startup tasks
        """

parse()
*******

This function is what the user will call to parse their file,
:code:`self.file_name`. The output should be a tuple of Steno3D Projects.
It is recommended to allow a Steno3d Project as input so files can be
parsed directly into an existing Project. However this behavior is not
required if it does not make sense for a certain file type.

Any errors encountered during parsing should raise a
:code:`steno3d.parsers.ParseError` with a descriptive error message. This
may include unsupported features, unrecognized features, incorrect
syntax in the input file, invalid geometry extracted from the file, etc.

Beyond that, the parse function may use anything else necessary to
read the file such as helper functions, additional classes you define, or
other imported modules.

AllParsers
**********

If a parser class is defined correctly, it will automatically become
available to :code:`steno3d.parsers.AllParsers` with its corresponding
extension. However, if you are making a large library of related parsers,
you may wish to define your own class similar to AllParsers internal to
your library. To do this, simply define a class that that inherits
AllParsers and contains a dictionary of extensions and appropriate
parser:

.. code::

    class ex1(steno3d.parsers.BaseParser):
        extensions = ('ex1',)
        ...

    class ex2(steno3d.parsers.BaseParser):
        extensions = ('ex2',)
        ...

    class ex3(steno3d.parsers.BaseParser):
        extensions = ('ex3',)
        ...

    class exN(steno3d.parsers.AllParsers):
        extensions = {
            'ex1': ex1,
            'ex2': ex2,
            'ex3': ex3
        }

You can then use this as:

.. code::

    >> ex1_parser = steno3d.parsers.exN('file.ex1')
    >> ex2_parser = steno3d.parsers.exN('file.ex2')
    >> ex3_parser = steno3d.parsers.exN('file.ex3')


If you run into issues, `report them on github <https://github.com/3ptscience/steno3dpy/issues/new>`_.
