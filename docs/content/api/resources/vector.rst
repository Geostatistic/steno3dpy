.. _resources_vector:

Vector
******

Steno3D Vectors are points in space with an associated direction. Currently,
vector magnitude is unsupported, only direction.

.. autoclass:: steno3d.vector.Vector
  :noindex:

Meshes
------

Vectors use the same mesh as Points.

.. autoclass:: steno3d.point.Mesh0D
  :noindex:

Data
----

The intended method of binding data to points is simply using a dictionary
containing location (nodes/vertices, 'N', is the only available location
for vectors) and data, a :ref:`DataArray <resources_data>`.

.. code:: python

    >> ...
    >> my_vector = steno3d.Vector(...)
    >> ...
    >> my_data = steno3d.DataArray(
           title='Six Numbers',
           array=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
       )
    >> my_vector.data = [dict(
           location='N',
           data=my_data
       )]

Under the surface, this dictionary becomes a :code:`_PointBinder` since
Vectors use the same mesh as Points.

Binding data to Vectors requires the data array to correspond to mesh
vertices.

.. autoclass:: steno3d.point._PointBinder
  :noindex:

Options
-------

Similar to data, options are intended to be constructed simply as a
dictionary.

.. code:: python

    >> ...
    >> my_vector = steno3d.Vector(...)
    >> ...
    >> my_vector.opts = dict(
           color='red',
           opacity=0.75
       )

This dictionary then becomes `_VectorOptions`.

.. autoclass:: steno3d.vector._VectorOptions
.. autoclass:: steno3d.point._Mesh0DOptions
  :noindex:
