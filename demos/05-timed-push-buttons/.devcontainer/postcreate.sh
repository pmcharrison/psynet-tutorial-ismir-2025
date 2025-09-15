# This script runs at the end of the container build process.

# There is a bug in GitHub Codespace that triggers the Git 'unsafe repository' error,
# due to a issue with how ownership is handled in the Codespace environment.
# We disable this check with the following command.
git config --global --add safe.directory '*'

# This /experiment directory is used when the Docker image is used as a base for deploying
# experiments, but when we are working in the Codespace, we instead want to use
# the workspaces directory as our working directory.
# rm -rf /experiment
