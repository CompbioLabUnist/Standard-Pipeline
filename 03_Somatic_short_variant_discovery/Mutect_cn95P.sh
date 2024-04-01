#!/bin/bash
/BiO/Share/Tools/gatk-4.4.0.0/gatk Mutect2 --reference /BiO/Share/Database/gatk-bundle/hg38/Homo_sapiens_assembly38.fasta --input /BiO/Research/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/cn95N.Sort.MarkDuplicates.BQSR.bam --input /BiO/Research/Standard-Pipeline/02_Data_pre-processing_for_variant_discovery/cn95P.Sort.MarkDuplicates.BQSR.bam --normal-sample cn95N --output /BiO/Research/Standard-Pipeline/03_Somatic_short_variant_discovery/cn95P.vcf --native-pair-hmm-threads 20