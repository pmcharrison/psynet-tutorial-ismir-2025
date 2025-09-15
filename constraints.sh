#!/bin/bash
# Manage constraints.txt using Dallinger's constraints generator
# Usage: bash constraints.sh generate
#        bash constraints.sh check

curl -s https://raw.githubusercontent.com/Dallinger/Dallinger/master/dallinger/constraints.py | uv run - "$@"

if [ "$1" = "generate" ]; then
    echo "Copying requirements.txt and constraints.txt to demo directories..."
    for demo_dir in demos/*/; do
        if [ -d "$demo_dir" ]; then
            echo "Copying to $demo_dir"
            cp requirements.txt "$demo_dir"
            cp constraints.txt "$demo_dir"
        fi
    done
    echo "Done copying files to demo directories."
fi
