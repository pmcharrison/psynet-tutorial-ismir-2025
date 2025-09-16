Timeline
========

The timeline determines the sequential logic of the experiment.
A timeline comprises a series of *timeline elements* that, by default, are
presented sequentially. For example, the following code displays a welcome
message to the participant, then displays them a randomly generated number:

.. code-block:: python

    Timeline(
        InfoPage("Welcome to the experiment!", time_estimate=5),

        CodeBlock(lambda participant: participant.var.set(
            "random_number",
            random.randint(0, 100)
        )),

        PageMaker(
            lambda participant: InfoPage(
                f"My random number is {participant.var.random_number}"
            ),
            time_estimate=5
        ),
    )

We will now talk through these different kinds of components in turn.

Timeline elements
-----------------

There are three main kinds of timeline elements:

* `Pages`_
* `Page makers`_
* `Code blocks`_


`Page makers`_ are like pages, but include content that is computed
when the participant's web page loads.
`Code blocks`_ contain server logic that is executed in between pages,
for example to assign the participant to a group or to save the participant's data.

Pages
^^^^^

Pages define the web page that is shown to the participant at a given
point in time, and have fixed content that is the same for all participants.
We covered them in detail in the previous topic, :doc:`03-pages`.

Page makers
^^^^^^^^^^^

Ordinary pages in the timeline have fixed content that is shared between all participants.
Often, however, we want to present content that depends on the state of the current participant.
This is the purpose of page makers.
A page maker is defined by a function that is called when the participant accesses the page.
For example, a simple page maker might look like the following:

.. code-block:: python

    from psynet.timeline import PageMaker

    PageMaker(
        lambda participant: InfoPage(f"You answered {participant.answer}."),
        time_estimate=5,
    )

.. note::

    The ``answer`` attribute stores the answer that the participant gave to the previous page.


Code blocks
^^^^^^^^^^^

Code blocks define code that is executed in between pages. They are defined in a similar
way to page makers, except they don't return an output. For example:

.. code-block:: python

    from psynet.timeline import CodeBlock

    CodeBlock(
        lambda participant: participant.var.set("score", 10)
    )

.. note::

    If you want to put a complex function in a code block then the lambda format above many not be appropriate.
    Instead you can use a named function:

    .. code-block:: python

        def set_score(participant):
            participant.var.set("score", 10)

        CodeBlock(set_score)

Code execution
--------------

It's important to be clear on PsyNet's code execution model, because this can be the source of subtle errors.

When the web server is launched, the ``experiment.py`` file is imported, meaning that all code within it is executed.
This execution only happens once for that server, no matter how many participants are tested.
This has implications for randomness. For example, if you write this:

.. code-block:: python

    # experiment.py

    import random
    import psynet.experiment
    from psynet.timeline import Timeline

    def get_timeline():
        return Timeline(
            InfoPage(
                f"My random number is {random.randint(0, 100)}",
                time_estimate=5
            )
        )


    class Exp(psynet.experiment.Experiment):
        timeline = get_timeline()

then ``get_timeline()`` will be called exactly once (when ``experiment.py`` is imported),
and so ``random.randint`` will be called just once,
and so every participant will see the same random number.
To address this issue, you could write something like this:

.. code-block:: python

    def get_timeline():
        return Timeline(
            PageMaker(
                lambda: InfoPage(f"My random number is {random.randint(0, 100)}"),
                time_estimate=5
            )
        )

However, a subtle problem with this is that page makers are called every time the page loads.
This means that, if the participant refreshes the page, they will see a different random value,
which may not be appropriate.

Instead, the best way to achieve this functionality is by combining a code block with a page maker.

.. code-block:: python

    def get_timeline():
        return Timeline(
            CodeBlock(
                lambda participant: participant.var.set(
                    "random_number",
                    random.randint(0, 100),
                )
            ),
            PageMaker(
                lambda participant: InfoPage(
                    f"My random number is {participant.var.random_number}",
                ),
                time_estimate=5,
            )
        )

This can all be summarized with the following principle:
data that is specific to a given participant should be set in code blocks and read in page makers.


