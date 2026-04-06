#!/usr/bin/env python3
import argparse
import os
import pandas
import tqdm


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="Input TSV")
    parser.add_argument("output", help="Output directory")
    parser.add_argument("--gene", help="Gene(s) to display", nargs="+")

    return parser.parse_args()

def main():
    args = parse_arguments()

    input_data = pandas.read_csv(args.input, sep="\t", index_col=0)
    print(input_data)

    for gene in tqdm.tqdm(args.gene):
        gene_data = input_data[(input_data["Hugo_Symbol"] == gene) & ~(input_data["HGVSp_Short"].isna())]
        print(gene_data)

        if gene_data.empty:
            continue

        proteins = ""
        for _, row in gene_data.iterrows():
            proteins += f"{row['HGVSp_Short'][2:]} "
        proteins = proteins.strip()

        os.system(f"/BiO/Share/Tools/lollipops -legend -labels -o {args.output}/{args.gene}.png -dpi=600 -show-motifs {gene} {proteins}")

if __name__ == "__main__":
    main()
