#!/bin/bash
mkdir -p Pathway
python3 07_7_check_pathway.py "$(realpath ./expression.tsv)" "$(realpath Pathway)"
