.. _resources_surface:

Surface
*******

.. image:: /images/steno3d_surface.png
    :width: 80%
    :align: center

Steno3D Surfaces are 2D resources. The steps to construct the surface resource
pictured above can be found online in the
`example notebooks <https://github.com/aranzgeo/steno3d-notebooks>`_.

.. autoclass:: steno3d.surface.Surface

Meshes
------

.. autoclass:: steno3d.surface.Mesh2D
.. autoclass:: steno3d.surface.Mesh2DGrid

Data
----

The intended method of binding data to surfaces is simply using a dictionary
containing location (either nodes/vertices, 'N', or cell centers/faces, 'CC')
and data, a :ref:`DataArray <resources_data>`.

.. code:: python

    >> ...
    >> my_surf = steno3d.Surface(...)
    >> ...
    >> my_data = steno3d.DataArray(
           title='Six Numbers',
           array=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
       )
    >> my_surf.data = [dict(
           location='N',
           data=my_data
       )]

Under the surface, this dictionary becomes a :code:`_SurfaceBinder`.

Binding data to a Surface using Mesh2D requires the data array to
correspond to mesh vertices or mesh triangles, for node and cell-center data,
respectively. When binding data to a Surface using Mesh2DGrid, you may specify
data order; the default is C-style, row-major ordering, but
Fortran-style, column-major ordering is also available. For more details
see the :ref:`DataArray documentation <resources_data>`.

.. autoclass:: steno3d.surface._SurfaceBinder

Options
-------

Similar to data, options are intended to be constructed simply as a
dictionary.

.. code:: python

    >> ...
    >> my_surf = steno3d.Surface(...)
    >> ...
    >> my_surf.opts = dict(
           color='red',
           opacity=0.75
       )

This dictionary then becomes `_SurfaceOptions`.

.. autoclass:: steno3d.surface._SurfaceOptions
.. autoclass:: steno3d.surface._Mesh2DOptions
