Pages
=====

The :doc:`02-pipelines` exercise introduced PsyNet experiments at a very high level.
We're now going to zoom in and start looking the individual building blocks that make up these experiments,
starting with pages.

PsyNet uses ``Page`` objects to represent what the participant sees at a given point in the experiment.
These ``Page`` objects are Python objects, all inheriting from the same ``Page`` base class.
Under the hood, the crucial method is ``Page.render``, which returns the HTML for the participant's current page.
If you wanted, you could customize this ``render`` method directly to make arbitrary pages.
In practice, though, most people use helper classes (e.g. ``InfoPage``, ``ModularPage``) that
provide pre-built implementations, and that's what we'll look at now.

Info pages
----------

The **info page** is the simplest type of page.
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

Modular pages
-------------

More complex pages can be designed using **modular pages**.
Modular pages work by combining together
a *prompt*, which defines some kind of content that is presented to the participant,
and a *control*, which defines how the user responds to that content.
PsyNet provides a library of built-in prompts and controls which in combination support
a great variety of experimental interfaces without the need to write custom HTML or JS.

For example, the following code defines a modular page that combines some text instructions
with a **push-button control** (i.e. a multiple-choice interface):

.. code-block:: python

    from psynet.modular_page import ModularPage, PushButtonControl

    ModularPage(
        label="push_button_page",
        prompt="Were those instructions clear?",
        control=PushButtonControl(
            choices=["Yes, they were clear", "Sorry, they were not clear"],
        ),
        time_estimate=5,
    )

This code demonstrate the use of an **image prompt**:

.. code-block:: python

    from psynet.modular_page import ModularPage, ImagePrompt

    ModularPage(
        label="image_prompt",
        prompt=ImagePrompt(
            "static/images/lake_mirror_reflection_yosemite.jpg",
            text="This is an example of an image prompt.",
            width="767px",
            height="512px",
            margin_bottom="25px",
        ),
        time_estimate=5,
    )

.. note::

    Here we have provided the ``ImagePrompt`` constructor with a path to an image in the `static` directory.
    This approach is suitable for one-off pages such as experiment instructions.
    However, for large numbers of files (e.g. experiment stimuli) you would normally use PsyNet's asset system instead.

The following example combines an **audio prompt** with a **text control**:
the participant hears the audio stimulus and then writes about it.

.. code-block:: python

    ModularPage(
        label="audio_prompt",
        prompt=AudioPrompt(
            "static/audio/clarinet.mp3",
            text="Listen to this audio stimulus",
        ),
        control=TextControl(),
        time_estimate=5,
    ),

Here's a considerably more complex example.
We play some audio (using an **audio prompt**) and then record from the participant's microphone
(using an **audio record control**).

.. code-block:: python

    from psynet.timeline import Event, ProgressDisplay, ProgressStage, Timeline

    ModularPage(
        label="audio_prompt_and_record",
        prompt=AudioPrompt(
            "static/audio/clarinet.mp3",
            text="Listen to the recording and then try and imitate it vocally.",
            play_window=[0, 3.0]
        ),
        control=AudioRecordControl(
            duration=3.0,
            bot_response_media="static/audio/clarinet.mp3",
        ),
        time_estimate=10.0,
        events={
            "recordStart": Event(is_triggered_by="promptEnd", delay=0.5),
        },
        progress_display=ProgressDisplay(
            stages=[
                ProgressStage([0.0, 3.0], "Listen...", "blue"),
                ProgressStage([3.0, 3.5], "Get ready...", "orange"),
                ProgressStage([3.5, 6.5], "Recording...", "red"),
                ProgressStage(
                    [6.5, 7.0], "Finished recording.", "blue", persistent=True
                ),
            ],
        )
    )

There are a few key features to point out in this example:

- We've used a ``play_window`` to enforce the duration of the audio prompt to be exactly 3.0 seconds.
- By default, the audio record control would start recording at the same time that the audio prompt starts.
  However, we've used the page's ``events`` parameter to specify that we instead want the ``recordStart``
  event to be triggered 0.5 seconds after the ``promptEnd`` event.
- We've used the page's ``progress_display`` parameter to design a **progress display** that will include
  both a progress bar and some progress text. This is helpful for showing the participant what to do when.

.. note::

    PsyNet progress bars are defined by proving a list of **progress stages**.
    A progress stage is defined by a start time, an end time, a caption, and a color.
    For example, the following code defines a progress stage lasting from
    3.0 to 3.5 seconds, displayed in orange, with the caption "Get ready...":

    .. code-block:: python

        ProgressStage([3.0, 3.5], "Get ready...", "orange")


.. warning::

    The timing of PsyNet web audio events is a little imprecise;
    you should try and make your implementation robust to these imprecisions.
    For example, in the example above we leave a silent buffer of 0.5 seconds between the
    prompt finishing and the recording starting to avoid bleedover betweeen the two.

Various other prompts and controls are available in the PsyNet package:

- ``VideoPrompt`` - Plays a video.
- ``ColorPrompt`` - Displays a color.
- ``JSSynth`` - Plays audio using a simple polyphonic synthesizer.
- ``GraphicPrompt`` - Displays programmatically generated animations.
- ``MusicNotationPrompt`` - Displays a snippet of Western music notation.
- ``GraphicControl`` - Like ``GraphicControl``, but the participant can click to respond.
- ``CheckboxControl`` - Multiple choices with checkboxes.
- ``RadioButtonControl`` - Multiple choices with radio buttons.
- ``DropdownControl`` - Multiple choices with a dropdown menu.
- ``SurveyJSControl`` - Supports the definition of multi-item surveys using the popular SurveyJS package.
- ``KeyboardPushButtonControl`` - A variant of ``PushButtonControl`` where you can respond with the keyboard.
- ``TimedPushButtonControl`` - A variant of ``PushButtonControl`` where you press buttons
  and the timing of those presses is recorded.
- ``SliderControl`` - Respond with a draggable slider.
- ``FrameSliderControl`` - A version of ``SliderControl`` where the slider seeks through the frames of a video.
- ``VideoRecordControl`` - Record a video.
- ``RatingControl`` - Respond with a rating scale.
- ``MultiRatingControl`` - Respond with multiple rating scales.


Exercises
---------

1. Navigate to the ``pages`` demo (``cd demos/features/01-pages``).
   Run this demo with ``psynet debug local``, and go through each page one at a time,
   relating the code in ``experiment.py`` to the user experience.
2. Go through the pages demo once more, but this time find the source code for the prompts/controls being called
   (you can do this in GitHub Codespaces/VSCode by selecting e.g. ``AudioPrompt`` and pressing F12).
   The source code will contain a variety of additional parameters;
   verify that you can change them and see the results when refreshing the browser.

.. warning::

    Most cosmetic changes will display when you refresh the page, but if you add files to the ``/static`` directory,
    you will need to stop the debug session (CTRL-C) and rerun ``psynet debug local``.

.. hint::

    To skip pages in the experiment, comment them out
    (select them in your IDE, then press Edit/Toggle line comment, or the corresponding keyboard shortcut).

3. Try creating a new modular page that combines a prompt and a control from the list above.

.. hint::

    To find out how to import and use a given PsyNet class, you can use the Q&A feature of the
    `PsyNet DeepWiki <https://deepwiki.com/pmcharrison/psynet-mirror>`_;
    it'll summarize the API for you and give you examples of its use.
    Alternatively, you can search PsyNet's `documentation website <https://psynet.dev>`_
    or the `PsyNet codebase <https://gitlab.com/PsyNetDev/psynet.git>`_ itself.

Further reading
---------------

.. note::

    In a live tutorial we recommend skipping this section for now and moving onto the next chapter.
    However, we recommend coming back to this section before you run a real PsyNet experiment.

Consent pages
^^^^^^^^^^^^^

Most academic institutions require experiments to obtain informed consent from the participant.
This typically involves explaining the study to the participants and confirming that they are willing to take part.
To define your own consent page, we recommend writing something like this:

.. code-block:: python

    from psynet.consent import Consent
    from psynet.page import InfoPage

    class CustomConsent(InfoPage, Consent):
        consent_text = """
        In this experiment you will be asked to ...

        This experiment involves no risk beyond...

        If you successfully complete the experiment, you will....
        """

        time_estimate = 60

        def __init__():
            return super().__init(consent_text, time_estimate=time_estimate)

.. note::

    When you deploy an experiment, PsyNet checks your timeline to see if you've included a consent,
    and will throw an error if you haven't.


End pages
^^^^^^^^^

**End pages** are used to signify the end of the experiment. There are two main types:
``SuccessfulEndPage`` and ``UnsuccessfulEndPage``.
Successful end pages do not normally need to be inserted explicitly; any participant who reaches
the end of the timeline will be considered a successful completion.
Unsuccessful end pages are more useful:
we can use them to declare that a given participant has failed the experiment and needs to exit early.

Custom classes
^^^^^^^^^^^^^^

It is also possible to define your own modular page classes.
This way you can have full flexibility about your experiment interface.
The first step is to create an HTML file in ``templates/``, perhaps called ``templates/custom-control.html``.
Here's an example...

.. code-block:: jinja

    // templates/custom-control.html

    {% macro color_text_area(params) %}

    <textarea id="text-input" type="text" class="form-control"></textarea>

    <style>
        #text-input {
            background-color: {{ params.color }};
            margin-bottom: {{ params.margin-bottom }};
        }
    </style>

    <script>
        function retrieveResponse() {
            return {
                rawAnswer: document.getElementById('text-input').value;
                metadata: {};
                blobs: {}
            }
        }
    </script>

    {% endmacro %}

There are a few key things to note here.

- The control is rendered using Jinja.
  Jina is a templating language that allows you to inject Python variables into HTML files.
- More specifically, the control takes the form of a Jinja macro called ``color_text_area``
  that takes a single input, ``params``.
- The control is specified like an ordinary HTML file, but the customizable aspects are acquired from the
  ``params`` object using curly bracket notation.
- The user must define a JS function called ``retrieveResponse`` that, when called, should return
  an object containing the following:

    - ``rawAnswer`` - The participant's answer in JSON-serializable form (numbers, strings, or an object comprising these).
    - ``metadata`` - Optional additional information about the response.
    - ``blobs`` - An optional dictionary of 'blobs', used for uploading media files (e.g. audio recordings).

The user must then define a corresponding class in Python, writing code like this:

.. code-block:: python

    # experiment.py

    from psynet.modular_page import Control

    class ColorTextAreaControl(Control):
        macro = "color_text_area"
        external_template = "custom-control.html"

        def __init__(self, color, **kwargs):
            super().__init__(**kwargs)
            self.color = color

        def format_answer(self, raw_answer, **kwargs):
            return super().format_answer(raw_answer, **kwargs)

        def get_bot_response(self, experiment, bot, page, prompt):
            return "Hello, I am a bot!"

There are a few more key things to note here:

- The ``macro`` and ``external_template`` attributes link to our Jinja template and the macro defined within it.
- The ``__init__`` method stores attributes that can later be accessed in the ``params`` template object.
- The ``format_answer`` method can optionally be used to clean up the submitted answer before saving it in the database.
- The ``get_bot_response`` method is used to simulate a bot's response to that control when running automated tests.

Defining custom prompts works in a similar way, except you don't need ``retrieveResponse``, ``format_answer``,
or ``get_bot_response``.

**Exercise**:
Think of an interesting prompt or control that is not listed above.
Implement it yourself using a custom template, and add it to the ``pages`` demo.

.. hint::

    If you are relatively new to HTML/CSS/JS, consider asking ChatGPT for help.
    It's particularly good at these kinds of small tasks.

Event management
^^^^^^^^^^^^^^^^

PsyNet has a special event management system that is used to manage modular components with a temporal aspect
(e.g. audio or video recorders). Most users don't need to worry about it, but it might be useful if you
get heavily into the customization side of PsyNet.
To learn more, read PsyNet's `event management documentation <psynetdev.gitlab.io/PsyNet/tutorials/event_management.html>`_.
