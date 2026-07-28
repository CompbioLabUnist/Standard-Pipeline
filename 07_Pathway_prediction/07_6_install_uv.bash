#!/bin/bash
uv venv --python python3 --prompt 'pathway' .venv
uv pip install --python .venv/bin/python --no-cache-dir --requirement 07_2_requirements.txt
