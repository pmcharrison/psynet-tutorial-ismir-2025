Pages
=====

The pipelines exercise (see :doc:`02-pipelines`) introduced PsyNet experiments at a very high level.
We're now going to zoom in and start looking the individual building blocks that make up these experiments,
starting with pages.

PsyNet uses ``Page`` objects to represent what the participant sees at a given point in the experiment.
These ``Page`` objects are Python objects, all inheriting from the same ``Page`` base class.
Under the hood, the crucial method is ``Page.render``, which returns the HTML for the participant's current page.
If you wanted, you could customize this ``render`` method directly to make arbitrary pages.
In practice, though, most people use helper classes (e.g. ``InfoPage``, ``ModularPage``) that
provide pre-built implementations.

InfoPage
--------

The ``InfoPage`` is the simplest type of page.
It's used to display text snippets to user without recording any response.
Here's an example:

.. code-block:: python

    from psynet.page import InfoPage

    InfoPage(
        """
        Welcome to the experiment!
        """,
        time_estimate=5,
    )

.. note::

    PsyNet pages are defined with ``time_estimate`` parameters.
    This parameter should correspond to how long you expect the average participant to spend on the page,
    in units of seconds, including any page loading overheads.
    These estimates are used for constructing progress bars as well as (optionally) determining participant payments.

Arbitrary HTML content can be specified using ``Markup``:

.. code-block:: python

    from markupsafe import Markup
    from psynet.page import InfoPage

    InfoPage(
        Markup(
            """
            Welcome to the <strong>experiment</strong>!
            """
        ),
        time_estimate=5,
    )

ModularPage
-----------

More complex pages can be designed using the ``ModularPage`` class.
Modular pages work by combining together
a *prompt*, which defines some kind of content that is presented to the participant,
and a *control*, which defines how the user responds to that content.
PsyNet provides a library of built-in prompts and controls which in combination support
a great variety of experimental interfaces without the need to write custom HTML or JS.

For example, the following code




Experiment implementations organize sequences of ``Page`` objects into *timelines*.
The timeline is linear by default, meaning that the participant proceeds methodically from one page to the next
until they reach the end of the experiment.
However, more complex control flows are possible; we'll talk about those later in :doc:`04-control-flow`.

