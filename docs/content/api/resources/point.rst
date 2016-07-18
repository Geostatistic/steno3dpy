.. _resources_point:

Point
*****

.. image:: /images/steno3d_point.png
    :width: 80%
    :align: center

Steno3D Points are 0D resources. The steps to construct the point resource
pictured above can be found online in the
`example notebooks <http://mybinder.org/repo/3ptscience/steno3dpy-notebooks>`_.

.. autoclass:: steno3d.point.Point

Meshes
------

.. autoclass:: steno3d.point.Mesh0D

Data
----

The intended method of binding data to points is simply using a dictionary
containing location (nodes/vertices, 'N', is the only available location
for points) and data, a :ref:`DataArray <resources_data>`.

.. code:: python

    >> ...
    >> my_point = steno3d.Point(...)
    >> ...
    >> my_data = steno3d.DataArray(
           title='Six Numbers',
           array=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
       )
    >> my_point.data = [dict(
           location='N',
           data=my_data
       )]

Under the surface, this dictionary becomes a `_PointBinder`.

.. autoclass:: steno3d.point._PointBinder

Options
-------

Similar to data, options are intended to be constructed simply as a
dictionary.

.. code:: python

    >> ...
    >> my_point = steno3d.Point(...)
    >> ...
    >> my_point.opts = dict(
           color='red',
           opacity=0.75
       )

This dictionary then becomes `_PointOptions`.

.. autoclass:: steno3d.point._PointOptions
.. autoclass:: steno3d.point._Mesh0DOptions
