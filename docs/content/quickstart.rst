.. _quickstart:

Getting Started
===============

Get up and running with Steno3D_! This page contains resources for installing
Steno3D, trying out a sample project yourself, and exploring
public projects.

- :ref:`install_steno3d`
- :ref:`a_first_project`
- :ref:`try_steno3d`

If you run into issues: `report them on github <https://github.com/3ptscience/steno3dpy/issues/new>`_.


.. _install_steno3d:

Install Steno3D
---------------

Want to start using Steno3D with your own data? It is available on
`pip <https://pypi.python.org/pypi/steno3d>`_:

.. code::

    pip install steno3d

or install from `source <https://github.com/3ptscience/steno3dpy>`_:

.. code::

    git clone https://github.com/3ptscience/steno3dpy.git
    python setup.py install

Example `Jupyter notebooks <http://jupyter.readthedocs.io/en/latest/install.html>`_
can be `cloned <https://github.com/3ptscience/steno3d-notebooks>`_
or you can follow along `online <http://mybinder.org/repo/3ptscience/steno3d-notebooks>`_
with the First Project below

.. code::

    git clone https://github.com/3ptscience/steno3d-notebooks.git


.. _a_first_project:

A First Project
---------------

Let's get started using Steno3D. The following demo project is available
online in a Jupyter notebook at `mybinder.org <http://mybinder.org/repo/3ptscience/steno3d-notebooks>`_,
no installation required.

Here, we will create a public project containing a surface, upload it, and explore it with Steno3D!

.. image:: /images/steno3dpy_screenshot.png
    :width: 80%
    :align: center
    :target: http://mybinder.org/repo/3ptscience/steno3d-notebooks

Start by importing Steno3D. If you are using the online notebooks
your environment should already be set up; otherwise, Steno3D is
:ref:`easy to install <install_steno3d>`.

.. code:: python

    >> import steno3d


.. _first_project_log_in:

Log In
******

Next, you need to login using your API developer key. If you do not have a Steno3D
account, you can `sign up <https://steno3d.com/signup>`_ and request a `developer key <https://steno3d.com/settings/developer>`_
associated with your account.

Then, login using this key within Python. You need to do this step even if you are
logged in to steno3d.com; the developer key and your website login are separate.

.. code:: python

    >> steno3d.login('this-is-a-demo-key')


.. note::

    By default, your developer key will be saved locally to default credentials
    file `~/.steno3d_client/credentials`. This allows future logins without
    manually entering your key::

        >> steno3d.login()

    You may specify a different credentials file with::

        >> steno3d.login('this-is-a-demo-key', credentials_file='/path/to/file')

    or you may opt to not save the developer key at all with::

        >> steno3d.login('this-is-a-demo-key', skip_credentials=True)

If you ever lose your key, you can always `generate a new one <https://steno3d.com/settings/developer>`_.


.. _first_project_create_resources:

Create Resources
****************

We start by creating a project

.. code:: python

    >> my_proj = steno3d.Project(
           title='Demo Project',
           description='My first project',
           public=True
       )

Here, we will create a topographic surface of a `sinc function <https://en.wikipedia.org/wiki/Sinc_function>`_. We will
use `numpy <http://docs.scipy.org/doc/numpy/reference/>`_ to do this.

.. code:: python

    >> import numpy as np
    >> topo = lambda X, Y: 50*np.sinc(np.sqrt(X**2. + Y**2.)/20.)

Next, we define our x and y coordinates to make the mesh

.. code:: python

    >> x = np.linspace(-100, 100., num=100.)
    >> y = np.linspace(-100., 100., num=100.)
    >> my_mesh = steno3d.Mesh2DGrid(
           h1=np.diff(x),
           h2=np.diff(y),
           O=np.r_[-100.,-100.,0.]
       )

and define the Z vertex topography of the mesh.

.. code:: python

    >> X, Y = np.meshgrid(x, y, indexing='ij')
    >> Z = topo(X, Y)
    >> my_mesh.Z = Z.flatten()

Right now, we have a 2D mesh. Let's create a surface with this mesh geometry.

.. code:: python

    >> my_surf = steno3d.Surface(
           project=my_proj,
           mesh=my_mesh
       )
    >> my_surf.title = 'Sinc Surface'
    >> my_surf.description = '3D rendering of sinc function in Steno3D'

You may want to put data on the mesh. In this case, we assign topography
(same as the Z-values of the mesh) as data on the nodes of the mesh

.. code:: python

    >> my_topo_data = steno3d.DataArray(
           title='Sinc function topography',
           array=my_mesh.Z
       )
    >> my_surf.data = [dict(
           location='N',
           data=my_topo_data
       )]


.. _first_project_upload:

Upload
******

In order to view our 3D data, we first need to upload it.
Prior to uploading, you can check that all required parameters are set and
valid

.. code:: python

    >> my_surf.validate()

and then upload the surface.

.. code:: python

    >> my_surf.upload()

This will return a URL where you can view it.


.. _first_project_explore:

View
****

There are two options for viewing, if you are using the Jupyter notebook you
can plot the surface inline. This allows you to inspect it and make sure
it is constructed correctly.

.. code:: python

    >> my_surf.plot()

Once you are happy with your upload, use the project URL to view, explore,
and share the project on `steno3d.com <https://steno3d.com>`_.

.. code:: python

    >> print(my_proj.url)


.. _try_steno3d:

Explore Steno3D
---------------

To give you a flavor of Steno3D's capabilities, you can `explore public Steno3D projects <https://steno3d.com/explore>`_

.. image:: /images/steno3d_explore.png
    :width: 80%
    :align: center
    :target: https://steno3d.com/explore


.. _Steno3D: https://steno3d.com
