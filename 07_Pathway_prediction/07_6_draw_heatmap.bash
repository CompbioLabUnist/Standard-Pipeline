#!/bin/bash
mkdir -p Heatmap
python3 07_6_draw_heatmap.py "$(realpath ./expression.tsv)" "$(realpath Heatmap)"
