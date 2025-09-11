FROM python:3.12-bookworm

RUN pip install uv

# Heroku CLI is currently needed to run `psynet test local`, this should change soon
RUN curl https://cli-assets.heroku.com/install.sh | sh

COPY requirements.txt requirements.txt
COPY *constraints.txt constraints.txt

RUN uv pip install -r constraints.txt --system
