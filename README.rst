Steno3D
*******

.. image:: https://travis-ci.org/3ptscience/steno3dpy.svg?branch=master
    :target: https://travis-ci.org/3ptscience/steno3dpy

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :alt: MIT License
    :target: https://github.com/3ptscience/steno3dpy/blob/master/LICENSE

.. image:: https://img.shields.io/badge/download-PyPI-yellow.svg
    :target: https://pypi.python.org/pypi/steno3d

.. image:: http://mybinder.org/badge.svg
    :target: http://mybinder.org/repo/3ptscience/steno3dpy-notebooks

Welcome to the Python client library for `Steno3D <https://www.steno3d.com>`_
by `3point Science <https://www.3ptscience.com>`_.

.. image:: https://raw.githubusercontent.com/3ptscience/steno3dpy/master/docs/images/steno3dpy_screenshot.png
    :width: 40%
    :align: center
    :alt: Steno3D in action
    :target: https://steno3d.com/

If you have not yet installed `Steno3D <https://www.steno3d.com>`_, simply

.. code:: bash

    pip install steno3d

You also need to `sign up for a Steno3D account <https://www.steno3d.com/signup>`_.
From there, you can `request a developer API key <https://www.steno3d.com/settings/developer>`_.

At that point, you can

.. code:: python

    import steno3d
    steno3d.login()

then start building your 3D project. API documentation is available on
`online <https://steno3d.com/docs>`_. Tutorials and
Examples are available as `notebooks <http://mybinder.org/repo/3ptscience/steno3dpy-notebooks>`_.
Steno3D is built with tab-completion in mind for interactive environments like
the Jupyter Notebook. Class documentation can also be accessed in the python environment
with `?` and tab completion.
