.. _resources_volume:

Volume
******

.. image:: /images/steno3d_volume.png
    :width: 80%
    :align: center

Steno3D Volumes are 3D resources. The steps to construct the volume resource
pictured above can be found online in the
`example notebooks <https://github.com/3ptscience/steno3dpy-notebooks>`_.

.. autoclass:: steno3d.volume.Volume

Meshes
------

.. autoclass:: steno3d.volume.Mesh3DGrid

Data
----

The intended method of binding data to volumes is simply using a dictionary
containing location (cell centers, 'CC', is the only available location for
volumes) and data, a :ref:`DataArray <resources_data>`.

.. code:: python

    >> ...
    >> my_volume = steno3d.Volume(...)
    >> ...
    >> my_data = steno3d.DataArray(
           title='Six Numbers',
           array=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
       )
    >> my_volume.data = [dict(
           location='N',
           data=my_data
       )]

Under the surface, this dictionary becomes a :code:`_VolumeBinder`.

When binding data to a Volume, you may specify
data order; the default is C-style, row-major ordering, but
Fortran-style, column-major ordering is also available. For more details
see the :ref:`DataArray documentation<resources_data>`.

.. autoclass:: steno3d.volume._VolumeBinder

Options
-------

Similar to data, options are intended to be constructed simply as a
dictionary.

.. code:: python

    >> ...
    >> my_volume = steno3d.Volume(...)
    >> ...
    >> my_volume.opts = dict(
           color='red',
           opacity=0.75
       )

This dictionary then becomes `_VolumeOptions`.

.. autoclass:: steno3d.volume._VolumeOptions
.. autoclass:: steno3d.volume._Mesh3DOptions

