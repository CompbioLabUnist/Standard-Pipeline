#!/usr/bin/env python3
import argparse
import itertools
import matplotlib
import matplotlib.pyplot
import numpy
import pandas
import scipy
import seaborn
import statannotations.Annotator
import tqdm

p_threshold = 1e-5


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="Input merged TSV(.gz) file")
    parser.add_argument("output", help="Output directory")

    return parser.parse_args()


def main():
    args = parse_arguments()

    parameters = {"font.size": 50, "axes.labelsize": 50, "axes.titlesize": 75, "xtick.labelsize": 50, "ytick.labelsize": 50, "legend.fontsize": 30, "legend.title_fontsize": 30, "figure.dpi": 300, "text.color": "black", "font.family": "sans-serif", "pdf.fonttype": 42, "ps.fonttype": 42, "pdf.compression": 9}
    matplotlib.use("Agg")
    matplotlib.rcParams.update(parameters)
    seaborn.set_theme(context="poster", style="whitegrid", rc=parameters)

    expression_list = ["TPM", "FPKM"]
    cancer_type_dict = {"TNBC": ["K001_TT", "K002_TT", "K003_TT"], "TNAC": ["C001_TT", "C002_TT", "C003_TT"]}

    input_data = pandas.read_csv(args.input, sep="\t", index_col=0)
    gene_list = list(input_data.index)
    print(input_data)

    for expression, gene in tqdm.tqdm(list(itertools.product(expression_list, gene_list))):
        tnac_expression = input_data.loc[gene, list(map(lambda x: f"{x}-{expression}", cancer_type_dict["TNAC"]))]
        tnbc_expression = input_data.loc[gene, list(map(lambda x: f"{x}-{expression}", cancer_type_dict["TNBC"]))]

        if (numpy.std(tnac_expression) < numpy.finfo(float).eps) or (numpy.std(tnbc_expression) < numpy.finfo(float).eps):
            continue

        _, p_value = scipy.stats.ttest_ind(tnac_expression, tnbc_expression)
        if p_value >= p_threshold:
            continue

        drawing_data = pandas.DataFrame([("TNAC", e) for e in tnac_expression] + [("TNBC", e) for e in tnbc_expression], columns=["Type", expression])

        fig, ax = matplotlib.pyplot.subplots(figsize=(18, 18))

        ax = seaborn.barplot(data=drawing_data, x="Type", hue="Type", y=expression, hue_order=["TNAC", "TNBC"], palette={"TNAC": "tab:red", "TNBC": "tab:blue"}, ax=ax)
        statannotations.Annotator.Annotator(ax, [("TNAC", "TNBC")], data=drawing_data, x="Type", hue="Type", y=expression, hue_order=["TNAC", "TNBC"]).configure(test="t-test_ind", text_format="full", loc="inside", comparisons_correction=None, verbose=0).apply_and_annotate()

        matplotlib.pyplot.title(gene)
        matplotlib.pyplot.ylabel(f"{gene} ({expression})")

        matplotlib.pyplot.tight_layout()
        fig.savefig(f"{args.output}/{gene}-{expression}.pdf")
        fig.savefig(f"{args.output}/{gene}-{expression}.png")
        matplotlib.pyplot.close(fig)


if __name__ == "__main__":
    main()
