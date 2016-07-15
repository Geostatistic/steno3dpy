.. _resources_texture:

Texture
*******

In Steno3D, txtures are data that exist in space and are mapped to their corresponding
resources. Unlike data, they do not need to correspond to mesh nodes or
cell centers. This image shows how textures are mapped to a surface. Their
position is defined by an origin, O, and axis vectors, U and V, then they
are mapped laterally to the resource position.

.. image:: /images/texture_explanation.png

.. autoclass:: steno3d.texture.Texture2DImage
