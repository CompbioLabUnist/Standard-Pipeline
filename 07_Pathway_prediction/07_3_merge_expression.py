#!/usr/bin/env python3
import argparse
import os
import pandas
import tqdm


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="Input genes.results file(s)", nargs="+")
    parser.add_argument("output", help="Output TSV(.gz) file")

    return parser.parse_args()


def main():
    args = parse_arguments()

    expression_list = ["expected_count", "TPM", "FPKM"]

    gene_set = set()
    for input_file in tqdm.tqdm(args.input):
        input_data = pandas.read_csv(input_file, sep="\t", index_col=0)
        gene_set |= set(input_data.index)

    output_data = pandas.DataFrame(index=sorted(gene_set), dtype=float)
    for input_file in tqdm.tqdm(args.input):
        sample_name = os.path.basename(input_file).split(".")[0]
        input_data = pandas.read_csv(input_file, sep="\t", index_col=0)

        for expression in expression_list:
            output_data.loc[input_data.index, f"{sample_name}-{expression}"] = input_data[expression]
    print(output_data)
    output_data.to_csv(args.output, sep="\t")


if __name__ == "__main__":
    main()
