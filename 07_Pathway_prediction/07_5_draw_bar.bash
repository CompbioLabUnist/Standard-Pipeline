#!/bin/bash
mkdir -p Bar
python3 07_5_draw_bar.py "$(realpath ./expression.tsv)" "$(realpath Bar)"
