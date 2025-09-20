# Timed Push Button demo

## Overview

This is a demo of the 'Timed Push Button paradigm' using the PsyNet framework.

## Challenges to try out

- Try replacing the music stimuli with a set of your own
- Try replacing different types of response for participants to provide (see [Modular Pages](https://psynetdev.gitlab.io/PsyNet/tutorials/modular_page.html))
- Explore demographic questionnaires embedded within PsyNet (see [Demography](https://psynetdev.gitlab.io/PsyNet/tutorials/demography.html)) and add some at the end of the experiment timeline

👑 Grand challenge

Say you want the participants to hear short snippets of the music they pressed the buttons for, where they can write about why they found that particular bit interesting. How would you modify the current implementation?


## Running the experiment

### GitHub Codespaces

The simplest way to work with this experiment is to run it in GitHub Codespaces.
To do so, navigate to the repository page in GitHub (you might be looking at it already),
and click the green "Code" button, click "Codespaces", and then click "Create a codespace on main". The codespace will take a while to start up, because it needs to install the
dependencies, but don't worry, this is a one-time process. Once the codespace is ready, you
can then launch the experiment in debug mode by running the following command in the terminal:

```bash
psynet debug local
```

Wait a moment, and then a browser window should open containing a link to the dashboard.
Click it, then enter 'admin' as both username and password, then press OK.
You'll now see the experiment dashboard.
Click 'Development', then 'New participant', to create a link to try the experiment
as a participant.

### Locally in a virtual environment

A more conventional approach is to instead run this demo locally in a virtual environment.
This is more involved as you have to install several related dependencies like Redis and PostgreSQL.
To do so, navigate to the [PsyNet website](https://psynet.dev) and follow the 'virtual environment'
installation instructions. We recommend using Python 3.12.10 for this (or double-check the recommended
version of Python specified in the `pyproject.toml` file in the PsyNet source directory).

### Other options

It should also be possible to load this repository using Devcontainers in an IDE such as VSCode.
In theory, this should function equivalently to GitHub Codespaces. However, this hasn't worked
so reliably for us yet, and we're still figuring out how to make it work better.
