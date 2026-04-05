#!/usr/bin/env python3
import argparse
import matplotlib
import matplotlib.pyplot
import numpy
import pandas
import scipy
import seaborn
import tqdm

p_threshold = -1 * numpy.log10(0.05)
fc_threshold = numpy.log2(1.0)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="Input merged TSV(.gz) file")
    parser.add_argument("output", help="Output directory")

    return parser.parse_args()


def main():
    args = parse_arguments()

    parameters = {"font.size": 50, "axes.labelsize": 50, "axes.titlesize": 75, "xtick.labelsize": 50, "ytick.labelsize": 50, "legend.fontsize": 30, "legend.title_fontsize": 30, "figure.dpi": 600, "text.color": "black", "font.family": "sans-serif", "pdf.fonttype": 42, "ps.fonttype": 42, "pdf.compression": 9}
    matplotlib.use("Agg")
    matplotlib.rcParams.update(parameters)
    seaborn.set_theme(context="poster", style="whitegrid", rc=parameters)

    expression_list = ["expected_count", "TPM", "FPKM"]
    cancer_type_dict = {"TNBC": ["K001_TT", "K002_TT", "K003_TT"], "TNAC": ["C001_TT", "C002_TT", "C003_TT"]}

    input_data = pandas.read_csv(args.input, sep="\t", index_col=0)
    gene_list = list(input_data.index)
    print(input_data)

    def fold_change(gene: str, expression: str) -> float:
        tnac_expression = numpy.mean(input_data.loc[gene, list(map(lambda x: f"{x}-{expression}", cancer_type_dict["TNAC"]))])
        tnbc_expression = numpy.mean(input_data.loc[gene, list(map(lambda x: f"{x}-{expression}", cancer_type_dict["TNBC"]))])

        if (tnac_expression == 0) or (tnbc_expression == 0):
            return 0.0

        return numpy.log2(tnac_expression / tnbc_expression)

    def ttest(gene: str, expression: str) -> float:
        tnac_expression = input_data.loc[gene, list(map(lambda x: f"{x}-{expression}", cancer_type_dict["TNAC"]))]
        tnbc_expression = input_data.loc[gene, list(map(lambda x: f"{x}-{expression}", cancer_type_dict["TNBC"]))]

        if (numpy.std(tnac_expression) == 0) or (numpy.std(tnbc_expression) == 0):
            return 1.0

        return -1 * numpy.log10(scipy.stats.ttest_ind(tnac_expression, tnbc_expression)[1])

    for expression in tqdm.tqdm(expression_list):
        expression_data = pandas.DataFrame(index=input_data.index)
        expression_data["logFC"] = list(map(lambda x: fold_change(x, expression), gene_list))
        expression_data["logp"] = list(map(lambda x: ttest(x, expression), gene_list))
        print(expression_data)

        ns_data = expression_data.loc[(expression_data["logp"] < p_threshold) | ((expression_data["logFC"] < fc_threshold) & (expression_data["logFC"] > - fc_threshold))]
        up_data = expression_data.loc[(expression_data["logp"] > p_threshold) & (expression_data["logFC"] > fc_threshold)]
        down_data = expression_data.loc[(expression_data["logp"] > p_threshold) & (expression_data["logFC"] < - fc_threshold)]

        fig, ax = matplotlib.pyplot.subplots(figsize=(18, 18))

        matplotlib.pyplot.scatter(x=ns_data["logFC"], y=ns_data["logp"], s=200, c="tab:gray", edgecolors=None, rasterized=True, label="NS")
        matplotlib.pyplot.scatter(x=up_data["logFC"], y=up_data["logp"], s=200, c="tab:red", edgecolors=None, rasterized=True, label="TNAC")
        matplotlib.pyplot.scatter(x=down_data["logFC"], y=down_data["logp"], s=200, c="tab:blue", edgecolors=None, rasterized=True, label="TNBC")

        matplotlib.pyplot.xlabel("log2(FoldChange)")
        matplotlib.pyplot.ylabel("-log10(p)")
        matplotlib.pyplot.legend(loc="lower left")

        matplotlib.pyplot.tight_layout()
        fig.savefig(f"{args.output}/{expression}.pdf")
        fig.savefig(f"{args.output}/{expression}.png")
        matplotlib.pyplot.close(fig)


if __name__ == "__main__":
    main()
