# syntax = docker/dockerfile:1.2

FROM registry.gitlab.com/psynetdev/psynet:v12.1.0

RUN mkdir /experiment
WORKDIR /experiment

COPY requirements.txt requirements.txt
COPY *constraints.txt constraints.txt

ENV SKIP_DEPENDENCY_CHECK=""
ENV DALLINGER_NO_EGG_BUILD=1

# Note: SKIP_CHECK_PSYNET_VERSION_REQUIREMENT=1 below will soon become unnecessary as we are removing
# verify_psynet_requirement() from check_constraints. For now, though it is still necessary,
# because the Docker image being used for this step lags behind the latest version of PsyNet.

# # Have commented out this check because it's awkward for users to respond to this when it happens
# # during the devcontainers build process.
# # If you see an error here, you probably need to run `bash docker/generate-constraints` and then try again.
# RUN SKIP_CHECK_PSYNET_VERSION_REQUIREMENT=1 psynet check-constraints

# Uninstall PsyNet and Dallinger because otherwise we can run into edge cases where pip decides
# that Dallinger/PsyNet doesn't need upgrading and then the editable version is left in place.
RUN python3 -m pip uninstall -y psynet
RUN python3 -m pip uninstall -y dallinger

RUN if [ -f constraints.txt ]; then \
        python3 -m pip install -r constraints.txt; \
    else \
        python3 -m pip install -r requirements.txt; \
    fi

COPY *prepare_docker_image.sh prepare_docker_image.sh
RUN if test -f prepare_docker_image.sh ; then bash prepare_docker_image.sh ; fi

COPY . /experiment

ENV PORT=5000

CMD dallinger_heroku_web
