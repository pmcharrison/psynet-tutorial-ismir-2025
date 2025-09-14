Pipelines
=========

One of the key applications of PsyNet is creating data collection 'pipelines'.
A pipeline is a standardized procedure that takes some stimuli as an input and
produces human data as an output.
For example, we might take a directory of audio files as an input and run it through
a 'rating' pipeline, where participants rate the audio files for pleasantness on a scale from 1 to 5.
When we deploy the pipeline, PsyNet handles tedious logistic details such as asset deployment and participant recruitment;
we simply wait for the experiment to complete and then download the data.

The purpose of this exercise is to show you how easy it is to take a pre-existing pipeline and
apply it to your own stimuli.
This repository contains several example pipelines designed specifically for audio stimuli:

- :doc:`01-simple-rating <../demos/01-simple-rating>`: Participants rate audio stimuli for specified attributes;
- :doc:`02-tapping <../demos/02-tapping>`: Participants tap to the beat of musical stimuli;
- :doc:`03-step-tag <../demos/03-step-tag>`: Participants collaboratively generate tags for audio stimuli;
- :doc:`04-similarity <../demos/04-similarity>`: Participants rate the similarity of audio stimuli.

All these pipelines work in the same way: the user specifies a directory of audio stimuli and the pipeline takes care of the rest.
Typically the directory is linked into the ``experiment.py`` file with some kind of glob pattern, like this:

.. code-block:: python

    for path in Path("data/instrument_sounds").glob("*.mp3")

For this exercise, your task will be to choose one of these pipelines and apply it to your own stimuli.
You are welcome to choose whichever pipeline you like; if you want something simple, go with the 'simple-rating' pipeline,
but if you think one of the other pipelines connects particularly well to your own research, go with that.

Steps
-----

1. Choose a pipeline from the list above.
2. Open the corresponding directory in your IDE (either in GitHub Codespaces or locally).
3. Copy your stimuli into the ``data/`` directory.
4. Update the ``experiment.py`` file to point to your stimuli.
5. Try the experiment by running ``psynet debug local``.

Hints
-----

- Before you start, make sure
