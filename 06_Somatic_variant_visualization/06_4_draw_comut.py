#!/usr/bin/env python3
import argparse
import collections
from comut import comut
import matplotlib
import pandas


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="Input merged TSV file")
    parser.add_argument("output", help="Output PDF file")

    return parser.parse_args()


def main():
    args = parse_arguments()

    input_data = pandas.read_csv(args.input, sep="\t", index_col=0)
    print(input_data)

    matplotlib.use("Agg")
    matplotlib.rcParams.update({"font.size": 50, "axes.labelsize": 50, "axes.titlesize": 75, "xtick.labelsize": 50, "ytick.labelsize": 50, "legend.fontsize": 30, "legend.title_fontsize": 30, "figure.dpi": 600, "text.color": "black", "font.family": "sans-serif", "pdf.fonttype": 42, "ps.fonttype": 42, "pdf.compression": 9})

    sample_list = sorted(set(input_data["Tumor_Sample_Barcode"]))
    print(sample_list)

    mutation_counter = collections.Counter(input_data["Hugo_Symbol"])
    print(mutation_counter.most_common(10))

    my_comut = comut.CoMut()
    my_comut.samples = sample_list

    mutation_coloring = {"Missense_Mutation": "darkgreen", "Nonsense_Mutation": "cyan", "In_Frame_Ins": "navy", "In_Frame_Del": "navy", "Frame_Shift_Ins": "gold", "Frame_Shift_Del": "gold", "Splice_Site": "darkviolet", "Translation_Start_Site": "chocolate", "Nonstop_Mutation": "crimson", "Absent": "lightgray", "Multiple": "black"}

    gene_list = list(map(lambda x: x[0], mutation_counter.most_common(30)))
    selected_data = input_data.loc[(input_data["Hugo_Symbol"].isin(gene_list))]
    my_comut.add_categorical_data(selected_data[["Tumor_Sample_Barcode", "Hugo_Symbol", "Variant_Classification"]].set_axis(labels=["sample", "category", "value"], axis="columns"), name="Mutation type", category_order=gene_list[::-1], priority=["Frameshift indel"], mapping=mutation_coloring)

    my_comut.plot_comut(x_padding=0.04, y_padding=0.04, tri_padding=0.03, figsize=(32, 24))
    my_comut.add_unified_legend()
    my_comut.figure.savefig(args.output.replace(".pdf", ".png"), bbox_inches="tight")
    my_comut.figure.savefig(args.output, bbox_inches="tight")


if __name__ == "__main__":
    main()
