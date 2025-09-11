# PsyNet workshop ISMIR 2025

## Installation

### GitHub Codespaces

The simplest way to work with this collection of experiments is to run it in GitHub Codespaces.
To do so, navigate to the repository page in GitHub (you might be looking at it already),
and click the green "Code" button, click "Codespaces", and then click "Create codespace on main". The codespace will take a while to start up, because it needs to install the
dependencies, but don't worry, this is a one-time process.

Once the codespace is ready, choose an experiment you want to run from the `demos` directory.
Let's say we want to run the simple-rating experiment. We can do this as follows:

```bash
cd ~/demos/01-simple-rating  # Change to the experiment directory
psynet debug local  # Launch the experiment in debug mode
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
installation instructions. Make sure to use the version of Python specified in `.python-version`.

### Other options

It should also be possible to load this repository using Devcontainers in an IDE such as VSCode.
In theory, this should function equivalently to GitHub Codespaces. However, this hasn't worked
so reliably for us yet, and we're still figuring out how to make it work better.
