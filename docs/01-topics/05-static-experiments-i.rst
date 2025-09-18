Static experiments
==================

Prerequisites
-------------

This chapter assumes you have read the preceding chapters (particularly :doc:`03-pages`);
it also assumes you are familiar with Python subclassing and list comprehensions.

Introduction
------------

In PsyNet, we define a *static experiment* as an experiment where the stimuli stay fixed over time.
Many experiments fit into this mould, including several of our demos:

- :doc:`01-simple-rating <../02-demos/pipelines/01-simple-rating>`: Participants rate audio stimuli for specified attributes;
- :doc:`02-tapping <../02-demos/pipelines/02-tapping>`: Participants tap to the beat of musical stimuli;
- :doc:`04-similarity <../02-demos/pipelines/04-similarity>`: Participants rate the similarity of audio stimuli;
- :doc:`05-timed-push-buttons <../02-demos/pipelines/05-timed-push-buttons>`: Participants press buttons at interesting moments in audio stimuli.

PsyNet provides extensive support for implementing static experiments.
There is some initial overhead in learning the relevant concepts, but once you are familiar with these,
you will find you can implement a great variety of experiments very efficiently.
What's more, many of these concepts generalize to more complex paradigms,
such as chain experiments (see e.g. :doc:`03-step-tag <../02-demos/pipelines/03-step-tag>`).

Overview of concepts
--------------------

The implementation of static experiments in PsyNet relies on a collection of base classes:

- ``StaticNode``:
  A node provides the specification for a single stimulus.
- ``StaticTrial``:
  A trial represents a moment when a participant is presented with a stimulus and asked to provide a response.
- ``StaticTrialMaker``:
  The trial maker determines the logic in which trials are presented to the participant.
- ``Asset``:
  Assets are used to represent media files.

Experimenters customize these classes in various ways to define their experiment.
In this chapter, we will talk through each of these classes in detail,
using the :doc:`simple rating <../02-demos/pipelines/01-simple-rating>` pipeline as a starting point.

Nodes
-----

Nodes specify the stimuli that will be presented to the participant.
Each node contains two key attributes:

- `definition` -
  A dictionary of information about the stimulus, e.g. ``{"instrument": "clarinet"}``.
- `assets` -
  An optional dictionary of assets (i.e. media files).

In a static experiment, the nodes are typically specified by defining a ``get_nodes`` function
that returns a list of nodes.
In the :doc:`simple rating <../02-demos/pipelines/01-simple-rating>` experiment,
``get_nodes`` constructs a list comprehension over the ``.mp3`` files in ``data/instrument_sounds``:

.. code-block:: python

    def get_nodes():
        return [
            StaticNode(
                definition={
                    "stimulus_name": path.stem
                },
                assets={
                    "stimulus_audio": asset(path, cache=True),  # reuse the uploaded file between deployments
                },
            )
            for path in STIMULUS_DIR.glob(STIMULUS_PATTERN)
        ]

    STIMULUS_DIR = Path("data/instrument_sounds")
    STIMULUS_PATTERN = "*.mp3"

Nodes are implemented as database-backed objects using SQLAlchemy.
This means that, when the experiment is running, you can see each node as a row in the database (see the Database tab in the dashboard).

There are several ways to access nodes when the experiment is running:

.. code-block:: python

    StaticNode.query.all()  # pull all nodes from the database
    StaticNode.query.filter_by(trial_maker_id = "xxx").all()  # get all nodes for trial maker xxx
    trial.node  # get the node that the trial belongs to

Trials
------

Every trial is associated with one participant and one parent node.
The trial automatically inherits the ``definition`` and ``assets`` attributes from the node.

When implementing a static experiment, we do not typically instantiate trials directly;
we leave that up to the trial maker.
However, we do need to define a custom trial class that determines the logic for the trial.
This is done by subclassing PsyNet's ``StaticTrial`` class. We'll see an example in a moment.

When creating our custom subclass, we must implement two methods in particular:

- ``show_trial`` -
  determines the page that is shown to the participant.
- ``time_estimate`` -
  an estimated duration for that class of trials.

We can achieve further customization by implementing the following optional methods:

- ``finalize_definition`` -
  customizes the trial's definition over and above what is inherited from the node.
- ``score_answer`` -
  assigns a score to the participant's response.
- ``show_feedback`` -
  determines the page that is shown to the participant after the trial.
- ``analyze_recording`` -
  analyzes any recordings made during the trial.

Some of these will be discussed in more detail later in this chapter.

In the :doc:`simple rating <../02-demos/pipelines/01-simple-rating>` demo,
only the ``time_estimate`` and ``show_trial`` methods are implemented.
Here's how it's done:

.. code-block:: python

    # experiment.py

    class CustomTrial(StaticTrial):
        time_estimate = 10

        def show_trial(self, experiment, participant):
            return ModularPage(
                "ratings",
                AudioPrompt(
                    self.assets["stimulus_audio"],
                    "Please rate the sound. You can replay it as many times as you like.",
                    controls="Play",
                ),
                MultiRatingControl(
                    RatingScale(
                        name="brightness",
                        values=5,
                        title="Brightness",
                        min_description="Dark",
                        max_description="Bright",
                    ),
                    RatingScale(
                        name="roughness",
                        values=5,
                        title="Roughness",
                        min_description="Smooth",
                        max_description="Rough",
                    ),
                ),
                events={
                    "submitEnable": Event(is_triggered_by="promptEnd"),
                },
            )

Like nodes, trials are implemented as database-backed objects using SQLAlchemy.
Within a running experiment, you can access trials in various ways:

.. code-block:: python

    CustomTrial.query.all()  # pull all trials from the database
    node.all_trials # get all trials for a node
    participant.all_trials # get all trials for a participant

Trial makers
------------

The trial maker orchestrates the presentation of trials to the participant.
In the case of static experiments, we use the ``StaticTrialMaker`` class.
We instantiate the trial maker directly within the timeline:

.. code-block:: python

    def get_timeline():
        return Timeline(
            InfoPage(
                """
                In this experiment you will hear some sounds.
                Your task will be to rate them from 1 to 5 on several scales.
                """,
                time_estimate=5,
            ),
            StaticTrialMaker(
                id_="ratings",
                trial_class=CustomTrial,
                nodes=get_nodes,
                expected_trials_per_participant="n_nodes",
            ),
            InfoPage(
                "Thank you for your participation",
                time_estimate=5,
            ),
        )

There are three compulsory parameters for instantiating a static trial maker:

- ``id_`` -
  A string providing a unique identifier for the trial maker.
- ``trial_class`` -
  the custom trial subclass to use (see above).
- ``nodes`` -
  the ``get_nodes`` function that will generate our list of nodes (see above).
- ``expected_trials_per_participant`` -
  the number of trials we expect the average participant to take
  (used for time estimation),
  specified either as an integer or the string
  ``"n_nodes"`` (shorthand for the number of nodes in the trial maker). 

There are many other optional parameters available too. See in particular:

- ``max_trials_per_participant``
    Maximum number of trials that each participant may complete;
    once this number is reached, the participant will move on
    to the next stage in the timeline.
    This can either be an integer, or the string ``"n_nodes"``,
    which will be read as referring to the number of provided nodes.
- ``max_trials_per_block``
    Determines the maximum number of trials that a participant will be allowed to experience in each block,
    including failed trials. Note that this number does not include repeat trials.
- ``allow_repeated_nodes``
    Determines whether the participant can be administered the same node more than once.
- ``max_unique_nodes_per_block``
    Determines the maximum number of unique nodes that a participant will be allowed to experience
    in each block. Once this quota is reached, the participant will be forced to repeat
    previously experienced nodes.
- ``balance_across_nodes``
    If ``True`` (default), active balancing across participants is enabled, meaning that
    node selection favours nodes that have been presented fewest times to any participant
    in the experiment, excluding failed trials.
- ``check_performance_at_end``
    If ``True``, the participant's performance
    is evaluated at the end of the series of trials (see below for more information on performance checks).
    Defaults to ``False``.
- ``check_performance_every_trial``
    If ``True``, the participant's performance
    is evaluated after each trial.
    Defaults to ``False``.
- ``n_repeat_trials``
    Number of repeat trials to present to the participant. These trials
    are typically used to estimate the reliability of the participant's
    responses. Repeat trials are presented at the end of the trial maker,
    after all blocks have been completed.
    Defaults to 0.

Unlike nodes and trials, trial makers are not represented directly in the database,
though they are referred to in database rows like ``Node.trial_maker_id`` and ``Trial.trial_maker_id``.
During a running experiment, it is possible to access a given trial maker
with the following code:

.. code-block:: python

    from psynet.experiment import get_trial_maker

    get_trial_maker("xxx") # get the trial maker with ID "xxx"

Assets
------

Assets are PsyNet's way of representing and managing media files.
There are two main types of assets:
assets created from local files, and assets created from functions.
Both kinds can be created with the ``asset`` function.

Local file assets
^^^^^^^^^^^^^^^^^

Local file assets are created from existing files by passing the file path to ``asset``:

.. code-block:: python

    a = asset("data/audio_stimulus.mp3")

When the asset is deposited, PsyNet will ensure that a copy of this file exists in the app's storage service.

Function assets
^^^^^^^^^^^^^^^

Function assets are created by passing a function to ``asset``:

.. code-block:: python

    a = asset(generate_stimulus)

This function should accept a ``path`` argument corresponding to the path 
of the file to generate.
It can also request arguments that are keys in the node or trial's definition.

When the asset is deposited, PsyNet will run the function and deposit the output
in the app's storage service.

Just creating an asset object like this doesn't actually do anything;
the asset needs to be deposited first.
Depositing can be done manually by calling ``a.deposit()``.
However, in most situations one shouldn't need to do this manually.
If pre-defining assets as part of the timeline initialization, then it is sufficient to pass the
asset objects to the ``assets`` parameter of nodes, trial makers, or modules.
If defining assets on the fly as part of a trial, then one would typically call
``trial.add_assets`` instead.

In the context of ``show_trial``, assets can be accessed via the ``self.assets`` attribute of the trial.
These assets can then be passed directly to modular page prompts such as
``AudioPrompt`` or ``VideoPrompt``.
Alternatively, one can extract the public URL from ``asset.url``, and use this directly.

You can see what assets have been defined for your experiment by visiting the
Asset tabs in the dashboard's Database section.
You can also see how these files are being organized by inspecting the contents of ``~/psynet-data/assets``,
which is the default location for asset storage assuming that you haven't switched away
from the default 'local storage' configuration.

Advanced usage
--------------



To vary the definition on the trial level, we override the ``finalize_definition`` method of our custom Trial class.
For example, if we wanted to vary the volume and the pan slightly from trial to trial,
we might write something like this:

.. code-block:: python

    class CustomTrial(StaticTrial):
        def finalize_definition(self, definition, experiment, participant):
            definition["pan"] = random.uniform(-1.0, 1.0)
            definition["volume"] = random.uniform(0.75, 1.25)
            return definition

If we want to add assets that are specific to the trial (not just inherited from the node),
we should call ``add.assets`` within ``finalize_definition``.
Because these assets are being generated on the fly, we probably want to construct the asset from a function
rather than (just) a file path. So, we might extend the former example as follows:

.. code-block:: python

    from psynet.asset import asset

    class CustomTrial(StaticTrial):
        def finalize_definition(self, definition, experiment, participant):
            definition["pan"] = random.uniform(-1.0, 1.0)
            definition["volume"] = random.uniform(0.75, 1.25)
            self.add_assets({
                "modified_stimulus": asset(
                    self.generate_stimulus,
                    extension=".wav",
                )
            })
            return definition

        def generate_stimulus(self, path, pan, volume)
            original_audio_asset = self.node.assets["stimulus"]
            assert (
                isinstance(original_audio_asset.storage, LocalStorage),
                "generate_stimulus currently only supports LocalStorage"
            )
            original_audio_path = original_audio_asset.var.file_system_path
            sample_rate, audio = wavfile.read(original_audio_path)
            apply_pan(audio, pan)
            apply_volume(audio, volume)
            wavfile.write(path, sample_rate, audio)

Here we've defined a helper method called ``generate_stimulus`` that generates the trial's modified stimulus.
Under the hood, the asset system will call this method when the asset is needed,
providing as arguments the path for the desired output file as well as the contents from the trial's definition.
We use ``self.node.assets`` to access the parent node's assets,
and then use ``wavfile.read`` to read the original audio file.
We then apply the pan and volume adjustments to the audio, and write the result to the desired output file.

Blocks
------

The default behavior of a ``StaticTrialMaker`` is to administer a sequence of trials to the participant
where each successive trial is generated from a different node. By default, the nodes are chosen such that trials
accumulate evenly across nodes; in other words, we make sure that all nodes have 10 trials before allowing
any of the nodes to have 11 trials. However, this behavior is customizable in many different ways.

One way of customizing node selection is to organize nodes into blocks.
For example, we could write something like this:

.. code-block:: python

    def get_nodes():
        return [
            StaticNode(
                definition={"instrument": "violin"},
                block="strings",
            ),
            StaticNode(
                definition={"instrument": "cello"},
                block="strings",
            ),
            StaticNode(
                definition={"instrument": "double bass"},
                block="strings",
            ),
            StaticNode(
                definition={"instrument": "trumpet"},
                block="brass",
            ),
            StaticNode(
                definition={"instrument": "horn"},
                block="brass",
            ),
            StaticNode(
                definition={"instrument": "tuba"},
                block="brass",
            )
        ]

Here we have created a node for each instrument,
and assigned the instrument to a block corresponding to the instrument family (either strings or brass).
This means that PsyNet will 'block' the presentation of the stimuli, i.e. the participant will start
with stimuli from one family, then move to the next family, and so on.
This can be useful in certain experiments where you want participants to focus on subtle differences within
stimulus families rather than being distracted by differences between families.

By default, the block order will be randomized for each participant.
However, this behavior can be customized by creating a custom trial maker subclass
and overriding the ``choose_block_order`` method.
For example:

.. code-block:: python

    class CustomTrialMaker(StaticTrialMaker):
        def choose_block_order(self, experiment, participant, blocks):
            # Take the blocks in alphabetical order
            return sorted(blocks)

    CustomTrialMaker(
        id_="ratings",
        nodes=get_nodes,
        ...
    )

This technique can also be useful if you want to fix the order of stimuli in advance across all participants.
You would use logic like this:

.. code-block:: python

    def get_nodes():
        return [
            StaticNode(
                definition={"instrument": instrument},
                block=str(i)
            )
            for i, instrument in enumerate(["violin", "viola", "guitar", ...])
        ]

    class CustomTrialMaker(StaticTrialMaker):
        def choose_block_order(self, experiment, participant, blocks):
            # Present the stimuli in ascending numeric order of block.
            return sorted(blocks, key=int)


Participant groups
------------------

In an analogous fashion, it is possible to associate each node with a participant group.

.. code-block:: python

    [
        StaticNode(
            definition={"instrument": "trumpet"},
            participant_group="brass_players",
        ),
        StaticNode(
            definition={"instrument": "violin"},
            participant_group="string_players",
        ),
    ]

These nodes will then only be visited by participants within those respective participant groups.

By default, participants are randomly assigned to the participant groups defined within the node collection.
However, it is also possible to define some logic for assigning participants to groups.
Confusingly, the process is slightly different to how we customize block order assignment.
Rather than create a custom subclass, we instead pass a lambda function to the trial maker constructor,
something like this:

.. code-block:: python

    StaticTrialMaker(
        id_="ratings",
        nodes=get_nodes,
        choose_participant_group=lambda participant: participant.var.instrument_family
        ...
    )

The function should return a string corresponding to the group chosen for that participant.



Note how we have provided the trial maker with both the list of nodes and the customized trial class.

.. note::

    An important thing to note at this point is that the list of nodes is provided as a callable,
    not as a list. The reason why is a bit subtle. Our ``get_nodes`` function relies on listing the files in a directory,
    specifically a directory located within the ``data`` directory. Files within this directory are not included
    in the source code package that is deployed to the experiment server.
    This is intentional, because we want to keep the source code package light.
    That means that the file listing code will throw a ``FileNotFoundError`` if we run it on the experiment server.
    To get around this, we wrap it in a callable, meaning that it is only executed when required
    (i.e. in the pre-deploy phase, when uploading the experiment to the server).

Scoring responses
-----------------

Often it makes sense to assign scores to individual trials. This can be done by overriding
the ``score_answer`` method of the trial class.
For example:

.. code-block:: python

    class CustomTrial(StaticTrial):
        def score_answer(self, answer, definition):
            return int(answer == definition["correct_answer"])

Feedback
--------

It is also possible to provide feedback to the participant after each trial.
This can be done by overriding the ``show_feedback`` method of the trial class.
Note that this method can access the ``score`` computed by the ``score_answer`` method.
For example:

.. code-block:: python

    class CustomTrial(StaticTrial):
        def show_feedback(self, experiment, participant):
            if self.score == 1:
                text = "Correct!"
            else:
                text = "Incorrect."
            return InfoPage(text)

Performance checks
------------------

As noted above, it is possible to implement automated performance checks for trial makers.
A performance check assesses the trials that the participant has completed,
gives the participant a score, and decides whether or not that participant should be failed.
Typically a failed participant would be ejected from the experiment at that point.
This is helpful for implementing performance-based screening tasks.

To implement a performance check, one needs to create a custom subclass for the trial maker,
and define a custom ``performance_check`` method. Arbitrary logic is possible here,
but a straightforward pattern is to override the trial method ``score_answer``,
and then sum up the resulting scores in the ``performance_check`` method.
Something like this:

.. code-block:: python

    class CustomTrial(StaticTrial):
        def score_answer(self, answer, definition):
            return int(answer == definition["correct_answer"])

    class CustomTrialMaker(StaticTrialMaker):
        threshold_score = 5

        def performance_check(self, experiment, participant, participant_trials):
            # Mean score would be a reasonable alternative here
            # if we wanted to be flexible with the number of trials
            total_score = sum(t.score for t in participant_trials)
            return {
                "score": total_score,
                "passed": total_score > self.threshold_score
            }

    CustomTrialMaker(
        id_="ratings",
        nodes=get_nodes,
        check_performance_at_end=True,
    )

In order to enable the performance check, we need to set either ``check_performance_at_end=True`` or
``check_performance_every_trial=True``. Here we've done the former, which means that the performance check will be run once,
after the participant has completed the trial maker.

Recordings
----------

If you want to make media recordings during a trial, you can make ``show_trial`` return
a page containing an ``AudioRecordControl`` or ``VideoRecordControl``.
If you want PsyNet to additionally analyze recordings on-the-fly (e.g. to make performance checks),
then you should do the following:

1. Inherit from ``RecordTrial``.
    Use dual inheritance, e.g. ``class CustomTrial(StaticTrial, RecordTrial)``.
2. Define a custom ``analyze_recording`` method.
    This method should take the audio file as an input and
    (a) create an analysis dictionary and
    (b) save an analysis plot.
    For example:

    .. code-block:: python

        def analyze_recording(self, audio_file: str, output_plot: str):
            fs, audio = wavfile.read(audio_file)
            analysis = ...
            make_plot(analysis, output_plot)
            return analysis

Your analysis will be conducted in a background worker process and will be visible from the
dashboard monitoring tab.

By default PsyNet won't make the participant wait for the analyses to complete.
However, it can be useful to enforce waiting if your experiment logic depends on analysis outcomes:

- If you want to wait for the analysis to complete before showing trial feedback,
  set ``wait_for_feedback = True`` in your ``CustomTrial`` definition.
- If you want to wait for all trial analyses to complete before running the
  trial maker's 'end' performance check,
  set ``end_performance_check_waits = True`` in your custom trial maker definition.
