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

Mapping data to a mesh is staightforward for unstructured meshes (those defined
by vertices, segments, triangles, etc); the order of the data array simply
corresponds to the order of the associated mesh parameter. For grid meshes,
however, mapping 1D data array to the 2D or 3D grid is not as simple. The
easiest way to correctly align data is to start with a numpy array that is
size (x, y) for 2D data or size (x, y, z) for 3D data then use numpy's
flatten() function with default order 'C'. For in-depth examples
of binding data to resources please refer to the
`example notebooks <http://mybinder.org/repo/3ptscience/steno3dpy-notebooks>`_.

.. autoclass:: steno3d.data.DataArray
