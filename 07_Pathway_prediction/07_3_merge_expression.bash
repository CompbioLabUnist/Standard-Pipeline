#!/bin/bash
python3 07_3_merge_expression.py $(realpath ../05_RNAseq_gene_expression/*.genes.results) "$(realpath ./expression.tsv.gz)"
