Running a demo
==============

The goal of this exercise is to run a demo experiment in debug mode.
Once you have an experiment running in debug mode, it's easy to make small tweaks to the logistic
and test the results.

You have a couple of options for your programming environment.
If you are new to PsyNet, we recommend using GitHub Codespaces, a cloud-based development environment
that is quick to set up and requires no local installation of software.
More experienced users might prefer to install PsyNet locally in order to have more control over the environment.
We only recommend this latter option if you are already an experienced UNIX and Python user.

Setting up your environment
---------------------------

.. tab-set::

    .. tab-item:: GitHub Codespaces

        Open the accompanying repository in `GitHub <https://github.com/pmcharrison/psynet-workshop-ismir-2025>`_.
        This repository contains configuration files for GitHub Codespaces in ``.devcontainer/``.
        Click the green "Code" button, click "Codespaces", and then click "Create codespace on main".
        Optionally, we recommend clicking the "Install Codespaces" button to the right of your URL bar,
        which will make your Codespace pop out as a separate window.
        You will then have to wait a few minutes for the codespace to start up;
        you can check the progress by clicking the "Building codespaces" text in the bottom right.
        You can tell that the codespace is ready once you see a message that

        You can tell that the codespace is ready once files are visible in the
        Once the codespace is ready, choose an experiment you want to run from the ``demos/`` directory.
        Let's say we want to run the simple-rating experiment. We can do this as follows:

        .. code-block:: bash

            cd ~/demos/01-simple-rating  # Change to the experiment directory
            psynet debug local  # Launch the experiment in debug mode

    .. tab-item:: Local environment

        Content for local environment setup goes here.
