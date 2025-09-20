Chain experiments
=================

Introduction
------------

Chain experiments are a generalization of static experiments where the nodes change over time.
This unlocks a broader range of experiment paradigms, such as adaptive tests,
collaborative annotation, cultural evolution simulations, and more.
Past PsyNet projects have included paradigms such as:

- Step-Tag:
    Participants collaboratively refine a set of tags for a given stimulus.
- Iterated tapping:
    Participants recursively imitate rhythms tapped by themselves or by other participants,
    revealing motor and cognitive biases in rhythm perception and production.
- Iterated singing:
    Participants recursively imitate melodies sung by themselves or by other participants,
    revealing motor and cognitive biases in melody perception and production.
- Gibbs Sampling with People:
    Participants collaboratively edit stimuli to optimize for a semantic descriptor.
- Markov Chain Monte Carlo with People:
    Participants perform two-alternative forced choice judgments to optimize for a semantic descriptor.
- Genetic Algorithm with People:
    Implements a genetic algorithm where human judgments provide the objective function.
- Create and Rate:
    Participants create stimuli and other participants rate them.

Ready-made implementations of many of these paradigms are available already in the PsyNet codebase.
This tutorial will show you how to build such a paradigm from scratch.

Base classes
------------

Chain experiments use an analogous collection of base classes to static experiments:

- ``ChainNode``:
  A node provides the specification for a single stimulus.
- ``ChainTrial``:
  A trial represents a moment when a participant is presented with a stimulus and asked to provide a response.
- ``ChainTrialMaker``:
  The trial maker determines the logic in which trials are presented to the participant.

These classes share many aspects with their static counterparts,
but there also some key differences.

Chain nodes
-----------

Chain nodes are initialized in the same way as static nodes.
The only difference is that instead of writing ``get_nodes`` we typically write ``get_start_nodes``,
to reflect the fact that we are only defining the nodes' starting states.

The most important difference with chain nodes is that we need to implement a
``make_next_definition`` method. This method is called when it is time for the node to
transition to its next state; it should return the definition for the new node.

Typically ``make_next_definition`` will want to extract some information from the trials of the
existing node. We recommend accessing these trials using ``self.completed_and_processed_trials``,
which returns a list of all trials for that node that have received answers and have finished processing
(so that e.g. ``analyze_recording`` will have completed), excluding failed trials
(e.g. trials where an error occurred, or that have been invalidated for some other reason).

In the following example, ``make_next_definition`` carries over the question attribute of the previous node,
and also takes the mean answer from the node's trials:

.. code-block:: python

    class CustomChainNode(ChainNode):
        def make_next_definition(self):
            return {
                "question": self.definition["question"],
                "mean_rating": statistics.mean(float(t.answer) for t in self.completed_and_processed_trials)
            }

When writing this method, it can be useful to refer to ``self.degree``, which refers to the node's position
in the chain (the starting node has ``degree=0``, the next has ``degree=1``, and so on).
When calling ``make_next_definition``, ``self.degree`` will give the degree of the node that currently exists;
the next node will have degree ``self.degree + 1``.

Chain trials
------------

Chain trials are similar to static trials.
As before, one must specify a ``time_estimate`` parameter and a ``show_trial`` method.
See :doc:`05-static-experiments-i` for further information.

Chain trial makers
------------------

Chain trial makers share many parameters with static trial makers.
Here are some parameters that are different:

- ``chain_type`` -
  This can either be ``"within"`` or ``"across"``.
  In a within-participant chain, each participant has their own set of chains,
  which are created when the participant arrives.
  In an across-participant chain, chains are shared across all the participants
  in the participant group.
- ``start_nodes`` -
  Should receive a ``get_start_nodes`` function that returns a list of nodes.
  If ``chain_type="within"`` and ``get_start_nodes`` has a ``participant`` argument,
  then this will be populated with the participant whose chains are being created.
- ``max_nodes_per_chain`` -
  How many nodes constitutes a 'full' chain? Once the chain reaches this number of nodes
  then it won't grow any more.
- ``trials_per_node`` -
  How many trials should each node receive before moving to the next state?
- ``balance_across_chains`` -
  Whether trial selection should be actively balanced across chains,
  such that trials are preferentially sourced from chains with
  fewer valid trials.
- ``allow_revisiting_networks_in_across_chains`` -
  Whether participants are allowed to revisit the same chain twice in an across-participant design.
  Defaults to ``False``.

Example implementation
----------------------

Here is a simple implementation of an 'imitation-chain' paradigm implemented using this framework.

.. code-block:: python

    STORIES = [
        "A man walked to the park and saw a duck...",
        "It was a rainy day in London...",
    ]

    class CustomChainNode(ChainNode):
        def make_next_definition(self):
            return {
                "story": self.completed_and_processed_trials[0].answer
            }

    def get_start_nodes():
        return[
            CustomChainNode(
                definition={
                    "story": story,
                }
            )
            for story in STORIES
        ]

    class CustomTrial(ChainTrial):
        time_estimate = 60

        def show_trial(self, experiment, participant):
            return join(
                InfoPage(
                    f"""
                    Read the following story carefully:

                    {self.definition["story"]}
                    """,
                ),
                ModularPage(
                    "recall_story",
                    "Now recall the story in your own words.",
                    TextControl(),
                )
            )

    ChainTrialMaker(
        "stories",
        chain_type="across",
        get_start_nodes=get_start_nodes,
        expected_trials_per_participant="n_start_nodes",
        max_nodes_per_chain=10,
    )

Exercise
--------

Turn this example into a musical example.
Participants should hear a short sequence of pitches.
They should then try and write down what notes they hear.
This transcription should then form the basis for the melody that the next participant hears.

**Hints**:

- ``psynet.js_synth.JSSynth`` provides a simple way to play melodies in the browser.
  Alternatively, you could generate an audio file yourself in Python.
- As an initial implementation, you could have the participant write down the melody as MIDI note numbers.
  For a more advanced implementation, you could accept letter names (e.g. C, D, E)
  or perhaps scientific pitch notation (e.g. C4, D4, E4).
- You want to prevent participants from entering invalid melodies.
  To prevent this, create a custom subclass of ``TextControl`` with a custom ``validate`` function:

    .. code-block:: python

        class MelodyTextControl(TextControl):
            def validate(self, response, **kwargs):
                answer = response.answer
                if not self.is_valid_melody(answer):
                    return "Invalid melody, please write your melody in the following format: ..."
                return None

            def is_valid_melody(answer):
                ...
