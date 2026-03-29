#!/usr/bin/env python3
import argparse
import matplotlib
import matplotlib.pyplot
import pandas
import seaborn
import tqdm


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="Input merged TSV file")
    parser.add_argument("output", help="Output directory")

    return parser.parse_args()


def reverse_strand(code):
    match_nucleotide = {"A": "T", "T": "A", "C": "G", "G": "C", ">": ">", "-": "-"}
    return "".join(list(map(lambda x: match_nucleotide[x], code)))


def main():
    args = parse_arguments()

    parameters = {"font.size": 50, "axes.labelsize": 50, "axes.titlesize": 75, "xtick.labelsize": 50, "ytick.labelsize": 50, "legend.fontsize": 30, "legend.title_fontsize": 30, "figure.dpi": 600, "text.color": "black", "font.family": "sans-serif", "pdf.fonttype": 42, "ps.fonttype": 42, "pdf.compression": 9}
    matplotlib.use("Agg")
    matplotlib.rcParams.update(parameters)
    seaborn.set_theme(context="poster", style="whitegrid", rc=parameters)

    input_data = pandas.read_csv(args.input, sep="\t", index_col=0)
    print(input_data)

    mutation_set = {"C>A", "C>G", "C>T", "T>A", "T>C", "T>G"}
    mutation_list = []
    for _, row in tqdm.tqdm(input_data.iterrows(), total=len(input_data)):
        ref = row["Reference_Allele"]
        alt = row["Tumor_Seq_Allele2"]
        mutation = f"{ref}>{alt}"

        if (ref == "G") or (ref == "A"):
            mutation = reverse_strand(mutation)

        if mutation not in mutation_set:
            mutation_list.append("Indel")
        else:
            mutation_list.append(mutation)
    input_data["Mutation"] = mutation_list
    print(input_data)

    previous_position = 999999999
    distance_list = []
    for _, row in tqdm.tqdm(input_data.iterrows(), total=len(input_data)):
        distance = row["Start_Position"] - previous_position

        if distance < 0:
            distance_list.append(0)
        else:
            distance_list.append(distance)

        previous_position = row["Start_Position"]
    input_data["Distance"] = distance_list
    print(input_data)

    chromosome_list = "chr1 chr2 chr3 chr4 chr5 chr6 chr7 chr8 chr9 chr10 chr11 chr12 chr13 chr14 chr15 chr16 chr17 chr18 chr19 chr20 chr21 chr22 chrX chrY chrM".split()
    print(len(chromosome_list), chromosome_list)

    coloring = {"C>A": "tab:blue", "C>G": "tab:orange", "C>T": "tab:green", "T>A": "tab:purple", "T>C": "tab:brown", "T>G": "tab:olive", "Indel": "tab:gray"}

    for chromosome in tqdm.tqdm(chromosome_list):
        chromosome_data = input_data.loc[(input_data["Chromosome"] == chromosome) & (input_data["Distance"] != 0)]

        fig, ax = matplotlib.pyplot.subplots(figsize=(32, 18))

        seaborn.scatterplot(data=chromosome_data, x="Start_Position", y="Distance", hue="Mutation", style="Mutation", hue_order=list(coloring.keys()), palette=coloring, legend="full", edgecolor=None, s=600, ax=ax)

        matplotlib.pyplot.title(chromosome)
        matplotlib.pyplot.xlabel("Mutation position (bp)")
        matplotlib.pyplot.ylabel("Distance (bp)")
        matplotlib.pyplot.yscale("log", base=10)
        matplotlib.pyplot.legend(loc="lower left")

        matplotlib.pyplot.tight_layout()
        fig.savefig(f"{args.output}/{chromosome}.pdf")
        fig.savefig(f"{args.output}/{chromosome}.png")
        matplotlib.pyplot.close(fig)


if __name__ == "__main__":
    main()
