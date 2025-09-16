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
        You can tell that the codespace is ready once you see a message that says "Your Codespace is ready!".

        Once the codespace is ready, choose an experiment you want to run from the ``demos/`` directory.
        Let's say we want to run the simple-rating experiment. We can do this as follows:

        .. code-block:: bash

            cd $DEMOS/pipelines/01-simple-rating  # Change to the experiment directory
            psynet debug local  # Launch the experiment in debug mode

        Wait a few moments, and you should see a popup asking "Do you want Code to open the external website?"
        Click "Configure Trusted Domains", and click "Trust all domains (disable link protection)".
        You should see a page containing a link to the experiment dashboard.
        Click this link, then enter 'admin' as both username and password, then press OK.
        Click the "Development" tab, then click "New participant":
        this will open a new browser window containing the participant interface.

    .. tab-item:: Local environment

        Start by cloning the repository to your local machine.

        .. code-block:: bash

            git clone https://github.com/pmcharrison/psynet-workshop-ismir-2025.git
            cd psynet-workshop-ismir-2025

        Then, create a virtual environment and install the dependencies.

        .. code-block:: bash

            python -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt -c constraints.txt

        Install the Heroku CLI:

        .. code-block:: bash

            curl https://cli-assets.heroku.com/install.sh | sh

        Install `Docker <https://docs.docker.com/get-docker/>`_ (if you haven't got it already).

        Start PostgreSQL and Redis via Docker:

        .. code-block:: bash

            dallinger docker start-services

        Then, choose an experiment you want to run from the ``demos/`` directory.
        Let's say we want to run the simple-rating experiment. We can do this as follows:

        .. code-block:: bash

            cd demos/pipelines/01-simple-rating  # Change to the experiment directory
            psynet debug local  # Launch the experiment in debug mode

        ``psynet debug local`` runs on port 5000, which may be occupied already if you are using
        a Mac with AirPlay enabled. If you see an error about the port being occupied,
        you can add ``port = 5001`` (or another port of your choice) to your experiment's ``config.txt`` file
        and try again.

        If everything works successfully, a couple of browser windows should open, one containing the experiment dashboard,
        and the other containing the participant interface.
        If this doesn't happen, check the terminal output for any errors.

Once you have followed the instructions above, you will hopefully have managed to launch an experiment in debug mode.
Try taking a few pages as a participant, and check that the pages advance appropriately.

Viewing your data
-----------------

Once you have taken a few pages yourself, and ideally seen an experiment trial or two,
you can also check out the dashboard to see your own data.
Click the "Database" dropdown in the navbar and then select "Participant".
You should see a table containing one row, which corresponds to you as a participant.
Scroll to the right to see various attributes that have been stored.
If you click again on "Database" you should also see somewhere some variant of "Trial"
(e.g. "CustomTrial"), depending on the experiment you ran.
Click on this, and you should see one row for each trial you've seen so far.

Making changes to the experiment
--------------------------------

Your next task is to try making some minor changes to the experiment code.
For now, just limit yourself to changing the text displayed to the participant.
Look at the participant page currently visible, and try and find the part of your code
that is responsible for displaying it.
Change some of the text, then save the file, then refresh the participant page.
You should see the changes you made.

.. note::

    Cosmetic changes to experiment code (e.g. changing display text) can be viewed
    immediately by refreshing the participant page.
    More substantial changes (e.g. adding new stimuli) require you to stop the debug session
    and start a new one.

Shutting down the session
-------------------------

Once you are done with your debug session, you can shut it down by pressing Ctrl+C in the terminal.

Shutting down the Codespace
---------------------------

If you are using GitHub Codespaces, you can shut down the Codespace by clicking the blue Codespaces button in the bottom left,
then clicking "Stop Current Codespace". However, if you are continuing with the next exercises,
we recommend keeping the Codespace running, so that you don't have to wait for it to start up again.
If you want to reset your environment to its original state, you can enter ``git reset --hard`` into your terminal
(or, to be completely sure, you can delete the Codespace and create a new one).

