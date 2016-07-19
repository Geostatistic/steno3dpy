.. _resources_line:

Line
****

.. image:: /images/steno3d_line.png
    :width: 80%
    :align: center

Steno3D Lines are 1D resources. The steps to construct the line resource
pictured above can be found online in the
`example notebooks <http://mybinder.org/repo/3ptscience/steno3dpy-notebooks>`_.

.. autoclass:: steno3d.line.Line

Meshes
------

.. autoclass:: steno3d.line.Mesh1D

Data
----

The intended method of binding data to lines is simply using a dictionary
containing location (either nodes/vertices, 'N', or cell centers/segments,
'CC') and data, a :ref:`DataArray <resources_data>`.

.. code:: python

    >> ...
    >> my_line = steno3d.Line(...)
    >> ...
    >> my_data = steno3d.DataArray(
           title='Six Numbers',
           array=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
       )
    >> my_line.data = [dict(
           location='N',
           data=my_data
       )]

Under the surface, this dictionary becomes a `_LineBinder`.

.. autoclass:: steno3d.line._LineBinder


Options
-------

Similar to data, options are intended to be constructed simply as a
dictionary.

.. code:: python

    >> ...
    >> my_line = steno3d.Line(...)
    >> ...
    >> my_line.opts = dict(
           color='red',
           opacity=0.75
       )

This dictionary then becomes `_LineOptions`.

.. autoclass:: steno3d.line._LineOptions
.. autoclass:: steno3d.line._Mesh1DOptions
