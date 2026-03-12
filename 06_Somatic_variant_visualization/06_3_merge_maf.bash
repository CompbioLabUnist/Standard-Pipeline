#!/bin/bash
./bin/python3 06_3_merge_maf.py "$(realpath ../03_Somatic_short_variant_discovery/*.maf)" "$(realpath ./merged.tsv)"
