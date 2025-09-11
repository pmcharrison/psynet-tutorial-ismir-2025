#!/bin/bash
# Manage constraints.txt using Dallinger's constraints generator
# Usage: bash constraints.sh generate
#        bash constraints.sh check
curl -s https://raw.githubusercontent.com/Dallinger/Dallinger/master/dallinger/constraints.py | uv run - "$@"
