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
fc_threshold = numpy.log2(8.0)


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

    def fold_change(gene: str, expression: str) -> float:
        tnac_expression = numpy.mean(input_data.loc[gene, list(map(lambda x: f"{x}-{expression}", cancer_type_dict["TNAC"]))])
        tnbc_expression = numpy.mean(input_data.loc[gene, list(map(lambda x: f"{x}-{expression}", cancer_type_dict["TNBC"]))])

        if (tnac_expression == 0) or (tnbc_expression == 0):
            return 0.0

        return numpy.log2(tnac_expression / tnbc_expression)

    def ttest(gene: str, expression: str) -> float:
        tnac_expression = input_data.loc[gene, list(map(lambda x: f"{x}-{expression}", cancer_type_dict["TNAC"]))]
        tnbc_expression = input_data.loc[gene, list(map(lambda x: f"{x}-{expression}", cancer_type_dict["TNBC"]))]

        if (numpy.std(tnac_expression) < numpy.finfo(float).eps) or (numpy.std(tnbc_expression) < numpy.finfo(float).eps):
            return 1.0

        return -1 * numpy.log10(scipy.stats.ttest_ind(tnac_expression, tnbc_expression)[1])

    for expression in tqdm.tqdm(expression_list):
        expression_data = pandas.DataFrame(index=input_data.index)
        expression_data["logFC"] = list(map(lambda x: fold_change(x, expression), gene_list))
        expression_data["logp"] = list(map(lambda x: ttest(x, expression), gene_list))
        print(expression_data)

        up_data = expression_data.loc[(expression_data["logp"] > p_threshold) & (expression_data["logFC"] > fc_threshold)].sort_values("logFC", ascending=False)
        down_data = expression_data.loc[(expression_data["logp"] > p_threshold) & (expression_data["logFC"] < - fc_threshold)].sort_values("logFC")

        drawing_data = input_data.loc[list(up_data.index) + list(down_data.index), list(map(lambda x: f"{x}-{expression}", cancer_type_dict["TNAC"] + cancer_type_dict["TNBC"]))]
        print(drawing_data)

        g = seaborn.clustermap(data=drawing_data, figsize=(24, 18), col_colors=["tab:red" for _ in cancer_type_dict["TNAC"]] + ["tab:blue" for _ in cancer_type_dict["TNBC"]], row_cluster=True, col_cluster=True, standard_scale=0, cmap="PRGn", robust=True, xticklabels=False, yticklabels=False)

        g.ax_heatmap.set_xlabel(f"{drawing_data.shape[1]} samples")
        g.ax_heatmap.set_ylabel(f"{drawing_data.shape[0]} genes")

        g.savefig(f"{args.output}/{expression}.pdf")
        g.savefig(f"{args.output}/{expression}.png")
        matplotlib.pyplot.close(g.figure)


if __name__ == "__main__":
    main()
