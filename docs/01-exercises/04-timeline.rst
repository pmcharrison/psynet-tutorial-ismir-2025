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

Arbitrary participant state information can be stored in ``participant.var``.
There are two main ways of getting information from pages to ``participant.var``.
One is to use ``participant.answer`` as an intermediate representation:

.. code-block:: python

    from psynet.timeline import CodeBlock, Timeline
    from psynet.modular_page import ModularPage, PushButtonControl

    Timeline(
        ModularPage(
            "color",
            "What is your favorite color?",
            PushButtonControl(choices=["red", "green", "blue"]),
            time_estimate=10,
        )
        CodeBlock(lambda participant: participant.var.set(
            "favorite_color", participant.answer
        ))
    )

The other, simpler route is to use the page's ``save_answer`` parameter:

.. code-block:: python

    from psynet.timeline import Timeline
    from psynet.modular_page import ModularPage, PushButtonControl

    Timeline(
        ModularPage(
            "color",
            "What is your favorite color?",
            PushButtonControl(choices=["red", "green", "blue"]),
            time_estimate=10,
            save_answer="favorite_color",
        ),
    )



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

Control logic
-------------

By default, participant proceed through timelines in serial order.
However, PsyNet provides various control constructs that enable more complex ordering logic.

Conditional
^^^^^^^^^^^

The conditional construct decides what timeline logic to administer based on a boolean expression.
For example:

.. code-block:: python

    from psynet.timeline import conditional
    from psynet.modular_page import ModularPage, PushButtonControl

    Timeline(
        ModularPage(
            "choose_page",
            "What page do you want to see next?"
            PushButtonControl(choices=["page_1", "page_2"]),
            save_answer="choose_page",
        ),
        conditional(
            "choose_page",
            lambda participant: participant.var.choose_page == "page_1",
            logic_if_true=page_1,
            logic_if_false=page_2,
        )

    )

Switch
^^^^^^

The switch is a more advanced version of the conditional that is useful for choosing between more than two options:

.. code-block:: python

    from psynet.timeline import switch
    from psynet.modular_page import ModularPage, PushButtonControl

    Timeline(
        ModularPage(
            "choose_page",
            "What page do you want to see next?"
            PushButtonControl(choices=["page_1", "page_2", "page_3"]),
            save_answer="choose_page",
        ),
        switch(
            "choose_page",
            lambda participant: participant.var.choose_page,
            {
                "page_1": page_1,
                "page_2": page_2,
                "page_3": page_3,
            }
        )
    )

While loop
^^^^^^^^^^

While loops repeatedly administer some logic while a given test condition is satisfied.
In the following example, the while loop continues until ``randint`` returns a value greater than 5:

.. code-block:: python

    while_loop(
        "my_loop",
        lambda participant: participant.var.get("score", default=0) <= 5
        logic=join(
            CodeBlock(lambda participant: participant.var.set("score", random.randint(1, 10))),
            conditional(
                "feedback",
                lambda participant: participant.var.score <= 5,
                logic_if_true=InfoPage(f"You scored {participant.var.score}, bad luck.", time_estimate=5),
                logic_if_false=InfoPage(f"You scored {participant.var.score}, well done!", time_estimate=5),
            )
        ),
        expected_repetitions=2,
    )

Note that we have to tell ``while_loop`` how many repetitions we expect on average, so that it knows how much
time to estimate for that part of the timeline.

For loop
^^^^^^^^

For loops iterate over a list whose values are determined once the participant reaches that part in the timeline.
For example:

.. code-block:: python

    from psynet.timeline import Timeline, for_loop
    from psynet.modular_page, DropdownControl

    Timeline(
        ModularPage(
            "target_number",
            "What number would you like to count up to?",
            DropdownControl([1, 2, 3, 4, 5]),
            time_estimate=5,
            save_answer="target_number",
        ),
        for_loop(
            "counting",
            lambda participant: list(range(1, participant.var.target_number + 1)),
            lambda x: InfoPage(str(x), time_estimate=5),
            time_estimate_per_iteration=5,
            expected_repetitions=3,
        )
    )

Note that, similar to ``while_loop``, we need to specify the number of expected repetitions so that PsyNet can estimate
how long this part of the timeline will take.

Time estimates
--------------

It is considered good practice to pay online participants a fee that corresponds
approximately to a reasonable hourly wage, for example 10 GBP/hour.
PsyNet provides sophisticated functionality for applying such
payment schemes without rewarding participants to participate slowly.
When designing an experiment, the researcher must specify along with each
page a ``time_estimate`` argument, corresponding to the estimated time in seconds
that a participant should take to complete that portion of the experiment.
This ``time_estimate`` argument is used to construct a progress bar displaying
the participant's progress through the experiment and to determine the participant's
final payment.

.. note::

    If you want PsyNet not to display information about financial rewards to the participants,
    you can set ``display_reward = false`` in your experiment's ``config.txt``.


Combining elements
------------------

We normally define our timelines by defining a ``get_timeline`` function in ``experiment.py``
and then saving the output of this function in our ``Experiment`` class.

.. code-block:: python

    # experiment.py

    import psynet.experiment
    from psynet.timeline import Timeline, CodeBlock, PageMaker
    from psynet.page import InfoPage

    def get_timeline():
        return Timeline(
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

Once your experiment gets complicated, it's usually a good idea to build the timeline up
out of multiple intermediate objects. For example, you can write something like this:

.. code-block:: python

    import psynet.experiment
    from psynet.timeline import join
    from psynet.page import InfoPage

    instructions = join(
        InfoPage("First you will...", ...),
        InfoPage("Then you will...", ...),
        ...
    )
    debrief = join(
        InfoPage("In this experiment you...", ...),
        InfoPage("Your results will be helpful for...", ...),
    )

    def get_timeline():
        return join(
            instructions,
            debrief,
        )

    class Exp(psynet.experiment.Experiment):
        timeline = get_timeline()

Note the use of the ``join`` function to create and merge sequences of timeline elements.

Exercises
---------

Using the debugger
^^^^^^^^^^^^^^^^^^



Making a shopping game
^^^^^^^^^^^^^^^^^^^^^^


