#!/bin/bash
mkdir -p Lollipop
python3 06_6_draw_lollipop.py "$(realpath merged.tsv)" "$(realpath Lollipop)" --gene "TP53" "PIK3CA"
