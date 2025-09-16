Pipelines
=========

A key use case of PsyNet is creating data collection 'pipelines'.
We can define a pipeline as a standardized procedure that takes some stimuli
as an input and produces human data as an output.
For example, we might take a directory of audio files as an input and run it through
a 'rating' pipeline, where participants rate the audio files for pleasantness on a scale from 1 to 5.
When we deploy the pipeline, PsyNet handles tedious logistic details such as asset deployment and participant recruitment;
we simply wait for the experiment to complete and then download the data.

In PsyNet a pipeline is defined by creating an 'experiment directory',
namely a folder of source code files that define the architecture and logic of an experiment.
The most important of these files is the ``experiment.py`` file,
which contains the primary logic of the experiment;
we also have files like ``config.txt``, which contains configuration parameters,
``requirements.txt``/``constraints.txt`` which define our Python dependencies,
``Dockerfile`` which defines our system environment, and so on.

For this tutorial we have prepared a collection of pipelines designed expressly for audio stimuli.
However, it is perfectly possibly to design analogous pipelines for images, videos, or other
kinds of content.

Here's a list of those pipelines:

- :doc:`01-simple-rating <../02-demos/01-simple-rating>`: Participants rate audio stimuli for specified attributes;
- :doc:`02-tapping <../02-demos/02-tapping>`: Participants tap to the beat of musical stimuli;
- :doc:`03-step-tag <../02-demos/03-step-tag>`: Participants collaboratively generate tags for audio stimuli;
- :doc:`04-similarity <../02-demos/04-similarity>`: Participants rate the similarity of audio stimuli;
- :doc:`05-timed-push-buttons <../02-demos/05-timed-push-buttons>`: Participants press buttons at interesting moments in audio stimuli.

All these pipelines work in the same way: the user specifies a directory of audio stimuli and the pipeline takes care of the rest.
Typically the directory is specified with some code like this:

.. code-block:: python

  STIMULUS_DIR = "data/instrument_sounds"
  STIMULUS_PATTERN = "*.mp3"

.. note::

  File paths are typically specified relative to the root of the
  experiment directory, i.e. the directory containing the ``experiment.py`` file).
  However, if you want to point to files outside your experiment directory,
  you can use absolute paths (e.g. ``/Users/alex/corpora/megacorpus``).

For this exercise, your task will be to choose one of these pipelines and apply it to your own stimuli.
You are welcome to choose whichever pipeline you like; if you want something simple, go with the 'simple-rating' pipeline,
but if you think one of the other pipelines connects particularly well to your own research, go with that.

Steps
-----

1. Choose a pipeline from the list above.
2. Make sure you can run the corresponding demo (see :doc:`01-running-a-demo`).
3. Copy your stimuli into the ``data/`` directory.
4. Update the ``experiment.py`` file to point to your stimuli.
5. Try the experiment again by running ``psynet debug local``.

Tips
----

- If you change ``STIMULUS_DIR`` while ``psynet debug local`` is running,
  the changes will not be reflected in the experiment.
  Instead, you will need to stop the debug session (Ctrl+C) and start a new one.
- Normally you would not want to commit large numbers of audio files to a Git repository.
  To prevent such files from being committed, you can add them to the ``.gitignore`` file, for example:

  .. code-block:: python

    data/instrument_sounds

  However, you'd need to instruct the user to add those files manually to the repository
  after cloning it from GitHub.
  Other possibilities include using `Git-LFS <https://git-lfs.com/>`_,
  or storing the files in a separate directory on your machine.
  In practice, though, you can probably get away with up to 100 MB of audio just
  using ordinary Git.
- We call the audio files in these experiments 'assets'.
  PsyNet has a built-in system for managing assets separately from source code.
  By default it stores assets in a directory on the web server itself,
  though it is also possible to select an 'S3 storage' option, where assets are instead stored
  in an Amazon Web Services S3 bucket.

.. note::

  If you want full control over your audio files, you can bypass the asset management system altogether.
  You could either:

  (a) Place the files in the ``static/`` directory and access them like ``/static/filename.mp3``, or
  (b) Upload the files to an external storage system and code the URLs directly into the experiment.
