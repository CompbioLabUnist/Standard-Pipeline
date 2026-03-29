#!/bin/bash
mkdir -p Rainfall
python3 06_5_draw_rainfall.py "$(realpath ./merged.tsv)" "$(realpath ./Rainfall)"
