#!/usr/bin/env python3
import argparse
import os
import pandas
import tqdm


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="Input MAF file(s)", nargs="+")
    parser.add_argument("output", help="Output TSV file")

    return parser.parse_args()


def main():
    args = parse_arguments()

    input_mafs = list()
    for input_file in tqdm.tqdm(args.input):
        input_df = pandas.read_csv(input_file, sep="\t", skiprows=1)
        input_df["Sample"] = os.path.basename(input_file).split(".")[0]
        input_mafs.append(input_df)

    merged_maf = pandas.concat(input_mafs, ignore_index=True)
    print(merged_maf)

    nonsynonymous_mutations = {"Frame_Shift_Del", "Frame_Shift_Ins", "In_Frame_Del", "In_Frame_Ins", "Missense_Mutation", "Nonsense_Mutation", "Splice_Site", "Translation_Start_Site", "Nonstop_Mutation"}
    merged_maf = merged_maf.loc[(merged_maf["Variant_Classification"].isin(nonsynonymous_mutations))]
    print(merged_maf)

    chromosome_list = "chr1 chr2 chr3 chr4 chr5 chr6 chr7 chr8 chr9 chr10 chr11 chr12 chr13 chr14 chr15 chr16 chr17 chr18 chr19 chr20 chr21 chr22 chrX".split()
    merged_maf = merged_maf.loc[(merged_maf["Chromosome"].isin(chromosome_list))]
    print(merged_maf)

    merged_maf.to_csv(args.output, sep="\t")

if __name__ == "__main__":
    main()