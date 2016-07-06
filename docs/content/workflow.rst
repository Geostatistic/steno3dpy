:orphan:

.. _workflow:

User Workflow
*************

Logging in
==========

User access is controlled by a ``develKey``, which is a long unique
string associated with each user account. In order to set up a
connection to the live database, you only need to import the ``steno3d``
module and call the ``login()`` function::

    In [1]: import steno3d

    In [2]: steno3d.login()
    Welcome to steno3d, a client library for Steno3D

        In order to access the Steno3D API, you need to request
        a developer key from the Steno3D website. Please go to
        https://steno3d.com/settings/api, log in to the
        application (if necessary) and request a new key.

        When you are ready, please enter the key below, or reproduce this
        prompt by calling steno3d.login().

    Please enter your devel key > 4015309b-f4d9-4297-bc0a-48bb4c331c67

    Out[3]: 'Welcome User!'

The developer key is a unique string separated by dashes. Once you have
pasted in your developer key, you should have access through the Python
API.

Resource Construction
=====================

Uploading
=========

Sharing
=======

