#!/bin/bash

# Add git commit template
git config --local commit.template .gitmessage

# Intall poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -