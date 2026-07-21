#!/bin/bash
uv venv --python python3 --prompt 'somatic' .venv
uv pip install --python .venv/bin/python --no-cache-dir --requirement 06_2_requirements.txt
