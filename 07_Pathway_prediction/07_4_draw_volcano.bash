#!/bin/bash
mkdir -p Volcano
python3 07_4_draw_volcano.py "$(realpath ./expression.tsv.gz)" "$(realpath Volcano)"
