.. _resources_data:

Data
****

In Steno3D, binding data to resources requires both a DataArray and a
data binder. These binders are documented within each composite resource.
The binders provide information about where the data maps to the mesh.
In most cases the available mesh locations are 'N', nodes, and 'CC',
cell centers. The easiest way to do this binding is to use a dictionary
with entries 'location' (either 'N' or 'CC') and 'data' (the DataArray).

Additionally, a resource can have any number of associated data arrays;
simply provide a list of these data binder dictionaries.
Here is a code snippet to show data binding in action; this assumes
the surface contains a mesh with 9 vertices and 4 faces (ie a 2x2 square grid).

.. code:: python

    >> ...
    >> my_surface = steno3d.Surface(...)
    >> ...
    >> my_node_data = steno3d.DataArray(
           title='Nine Numbers',
           array=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
       )
    >> my_face_data = steno3d.DataArray(
           title='Four Numbers',
           array=[0.0, 1.0, 2.0, 3.0]
       )
    >> my_surface.data = [
           dict(
               location='N',
               data=my_node_data
           ),
           dict(
               location='CC',
               data=my_face_data
            )
       ]

Mapping data to a mesh is staightforward for unstructured meshes (those defined
by vertices, segments, triangles, etc); the order of the data array simply
corresponds to the order of the associated mesh parameter. For grid meshes,
however, mapping 1D data array to the 2D or 3D grid requires correct ordering.
The default ordering is C-style, row-major ordering. For one example of
correctly aligning data, start with a numpy array that is size (x, y) for
2D data or size (x, y, z) for 3D data then use numpy's flatten() function
with default order 'C'. Alternatively, you may specify data order='f'.
This is Fortran- or Matlab-style, column-major ordering. For in-depth examples
of binding data to resources please refer to the
`example notebooks <http://mybinder.org/repo/3ptscience/steno3dpy-notebooks>`_.

.. autoclass:: steno3d.data.DataArray
