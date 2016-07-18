.. _resources_texture:

Texture
*******

In Steno3D, textures are data that exist in space and are mapped to their corresponding
resources. Unlike data, they do not need to correspond to mesh nodes or
cell centers. This image shows how textures are mapped to a surface. Their
position is defined by an origin, O, and axis vectors, U and V, then they
are mapped laterally to the resource position.

.. image:: /images/texture_explanation.png

Like data, multiple textures can be applied to a resource. Simply provide a
list of textures.

.. code:: python

    >> ...
    >> my_surface = steno3d.Surface(...)
    >> ...
    >> my_tex_1 = steno3d.Texture2dImage(
           O=[0.0, 0.0, 0.0],
           U=[1.0, 0.0, 0.0],
           V=[0.0, 1.0, 0.0],
           image='image1.png'
       )
    >> my_tex_2 = steno3d.Texture2dImage(
           O=[0.0, 0.0, 0.0],
           U=[1.0, 0.0, 0.0],
           V=[0.0, 0.0, 1.0],
           image='image2.png'
       )
    >> my_surface.texutures = [
           my_tex_1,
           my_tex_2
       ]

.. autoclass:: steno3d.texture.Texture2DImage
