Psycopg slideshow at PGDay 2013
===============================

An experiment using Landslide__ to produce an `HTML5 slideshow`__.

.. __: https://github.com/adamzap/landslide
.. __: https://code.google.com/p/html5slides/

Usage
-----

In order to render the slideshow, just install Landslide and::

    cd slides
    make html
    make pdf    # This requires Prince, see Landslide docs

The slideshow has an interactive part with more complex requirements: you can
build the entire environment with::

    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt

Run the ``pushdemo.py`` script with a connection string as first argument
(hint: quote it)::

    python slides/pushdemo.py "user=postgres dbname=test"

Display the html slideshow.  At the demo page, connect to the same database
using psql and execute something like::

    NOTIFY data, 'blue';
    NOTIFY data, 'red';

