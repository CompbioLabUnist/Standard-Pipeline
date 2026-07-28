#!/bin/bash
uv venv --python python3 --prompt 'signature' .venv
uv pip install --python .venv/bin/python --no-cache-dir --requirement 08_2_requirements.txt
