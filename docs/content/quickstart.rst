.. _quickstart:

Quickstart
==========

Get up and running with Steno3D_! This page contains resources for trying
Steno3D_ starting in demo jupyter notebooks, instructions for installing
Steno3D_ and a sample first project.

- :ref:`try_steno3d`
- :ref:`install_steno3d`
- :ref:`a_first_project`

If you run into issues: `report it on github <https://github.com/3ptscience/steno3dpy/issues/new>`_.

.. _try_steno3d:

Try Steno3D
-----------

To give you a flavor of Steno3D_, you can

- `Explore public Steno3D projects <https://steno3d.com/explore>`_
- or `create a demo project in a jupyter notebook, no installation required <http://mybinder.org/3ptscience/steno3dpy>`_


.. TODO: replace this image with one of image of steno3D public explore page
.. TODO: activate steno3dpy github links once public (with _ at the end) here and in index.rst


.. image:: /images/first_project_in_notebook.png
    :width: 80%
    :align: center
    :target: https://steno3d.com/explore


.. _install_steno3d:

Install Steno3D
---------------

Steno3D_ is on `pip <https://pypi.python.org/pypi/steno3d>`_:

.. code::

    pip install steno3d

or install from `source <https://github.com/3ptscience/steno3dpy>`_

.. code::

    git clone https://github.com/3ptscience/steno3dpy.git
    python setup.py install


.. _a_first_project:

A First Project
---------------

The following example is available in a `notebook <http://mybinder.org/3ptscience/steno3dpy>`_

Here, we will create a public project containing a topographic surface of a
sinc function, upload it, and explore it with Steno3D_!

.. image:: /images/steno3dsinc.png
    :width: 80%
    :align: center
    :target: http://mybinder.org/3ptscience/steno3dpy

Once Steno3D_ is :ref:`installed <install_steno3d>`, you should be able to import it

.. code:: python

    >> import steno3d

.. _first_project_log_in:

Log In
******

Next, you need to login using your API key. If you do not have a Steno3D_
account, you can `sign up <https://steno3d.com/signup>`_ and request a `developer key <https://steno3d.com/settings/developer>`_.

Then, login with that key

.. code:: python

    >> steno3d.login('this-is-a-demo-key')


.. note::

    On most modern computers, the api key will be stored in your keychain, so
    next time you login to Steno3D_, you will not need to manually enter your key::

        >> steno3d.login()

If you ever lose your key, you can generate a new one at https://steno3d.com/settings/developer.


.. _first_project_create_resources:

Create Resources
****************

We start by creating a project

.. code:: python

    >> proj = steno3d.Project(title='Demo Project',
                              description='My first project',
                              public=True)

Here, we will create a topographic surface of a sinc function. We will use `numpy <http://docs.scipy.org/doc/numpy/reference/>`_ to do this.

.. code:: python

    >> import numpy as np
    >> topo = lambda X, Y: 50*np.sinc(np.sqrt(X**2. + Y**2.)/20.)

Next, we define our x,y coordinates to make the mesh.

.. code:: python

    >> x = np.linspace(-100, 100., num=100.)
    >> y = np.linspace(-100., 100., num=100.)
    >> mesh2d = steno3d.Mesh2DGrid(h1=np.diff(x), h2=np.diff(y), x0=np.r_[-100.,-100.,0.])

and define the Z locations of the mesh.

.. code:: python

    >> X, Y = np.meshgrid(x,y)
    >> Z = topo(X, Y)
    >> mesh2d.Z = Z.flatten(order = 'C')

Right now, we have a 2D mesh. You may want to put data on the mesh. In this
case, we assign topography (same as the Z-locations of the mesh) as data on the nodes of the mesh

.. code:: python

    >> surface = steno3d.Surface(project = proj, mesh = mesh2d)
    >> surface.data = dict(location='N',
                           data=mesh2d.Z)

and add a title and description

.. code:: python

    >> surface.title = 'Topo'
    >> surface.description = 'This is a sinc function'


.. _first_project_upload:

Upload
******

In order to use Steno3D_ to view our 3D data, we need to upload the model.
Prior to uploading, you can check that all required parameters are set and
valid using :code:`validate`

.. code:: python

    >> surface.validate()

and then upload the surface.

.. code:: python

    >> surface.upload()

This will return a url where you can view it.


.. _first_project_explore:

Explore
*******

.. image:: /images/first_project_in_notebook.png
    :width: 80%
    :align: center
    :target: http://mybinder.org/3ptscience/steno3dpy

There are two options for viewing, if you are using the jupyter notebook you
can plot the surface inline

.. code:: python

    >> surface.plot()

or entire project inline

.. code:: python

    >> proj.plot()

or get the url to view the project in your browser

.. code:: python

    >> proj.url



.. _Steno3D: https://steno3d.com
