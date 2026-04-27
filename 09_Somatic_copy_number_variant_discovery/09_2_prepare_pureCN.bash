#!/bin/bash
python3 09_2_prepare_pureCN.py $(realpath ../02_Data_pre-processing_for_variant_discovery/*.BQSR.bam) "$(realpath .)"
