.. _resources_data:

Data
****

In Steno3D, binding data to resources requires both a DataArray and a
data binder. These binders are documented within each composite resource.
The binders provide information about where the data maps to the mesh.
In most cases the available mesh locations are 'N', nodes, and 'CC',
cell centers. The easiest way to do this binding is to use a dictionary
with entries 'location' (either 'N' or 'CC') and 'data' (the DataArray).
Here is a code snippet to show data binding in action; this assumes
the surface contains a mesh with 5 vertices.

.. code:: python

    >> ...
    >> my_surface = steno3d.Surface(...)
    >> ...
    >> my_data = steno3d.DataArray([0.0, 1.0, 2.0, 3.0, 4.0])
    >> my_surface.data = dict(
           location='N',
           data=my_data
       )

.. autoclass:: steno3d.data.DataArray
