#!/usr/bin/env python3
import argparse
import json
import requests
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

        add_gene_set_url = "https://maayanlab.cloud/Enrichr/addList"
        get_pathway_url = "https://maayanlab.cloud/Enrichr/enrich"

        up_payload = {"list": (None, "\n".join(sorted(up_data.index))), "description": (None, "TNAC")}
        down_payload = {"list": (None, "\n".join(sorted(down_data.index))), "description": (None, "TNBC")}

        up_response = json.loads(requests.post(add_gene_set_url, files=up_payload).text)
        down_response = json.loads(requests.post(add_gene_set_url, files=down_payload).text)

        background = "KEGG_2026"
        up_pathway = json.loads(requests.get(f"{get_pathway_url}?userListId={up_response['userListId']}&backgroundType={background}").text)
        down_pathway = json.loads(requests.get(f"{get_pathway_url}?userListId={down_response['userListId']}&backgroundType={background}").text)

        columns = ["Rank", "Term name", "P-value", "Z-score", "Combined score", "Overlapping genes", "Adjusted p-value", "Old p-value", "Old adjusted p-value"]
        up_enrichment_data = pandas.DataFrame(up_pathway[background], columns=columns)
        down_enrichment_data = pandas.DataFrame(down_pathway[background], columns=columns)

        p_column = "P-value"
        up_enrichment_data = up_enrichment_data.loc[(up_enrichment_data[p_column] < 0.05)]
        down_enrichment_data = down_enrichment_data.loc[(down_enrichment_data[p_column] < 0.05)]

        fig, ax = matplotlib.pyplot.subplots(figsize=(32, 18))
        up_enrichment_data["-log10(P)"] = -1 * numpy.log10(up_enrichment_data[p_column])
        up_enrichment_data["Gene count"] = list(map(lambda x: len(x), list(up_enrichment_data["Overlapping genes"])))

        seaborn.scatterplot(data=up_enrichment_data, x="-log10(P)", y="Rank", size="Gene count", sizes=(100, 1000), hue="Z-score", palette="Reds", legend="brief")

        matplotlib.pyplot.grid(True)
        matplotlib.pyplot.yticks(up_enrichment_data["Rank"], up_enrichment_data["Term name"], fontsize="xx-small")
        matplotlib.pyplot.xlabel("-log10(Padj)")
        matplotlib.pyplot.ylabel(f"{len(up_enrichment_data)} pathways")
        matplotlib.pyplot.title(f"TNAC pathways in {background.replace('_', ' ')}")
        ax.invert_yaxis()

        matplotlib.pyplot.tight_layout()
        fig.savefig(f"{args.output}/{expression}-TNAC.pdf")
        fig.savefig(f"{args.output}/{expression}-TNAC.png")
        matplotlib.pyplot.close(fig)

        fig, ax = matplotlib.pyplot.subplots(figsize=(32, 18))
        down_enrichment_data["-log10(P)"] = -1 * numpy.log10(down_enrichment_data[p_column])
        down_enrichment_data["Gene count"] = list(map(lambda x: len(x), list(down_enrichment_data["Overlapping genes"])))

        seaborn.scatterplot(data=down_enrichment_data, x="-log10(P)", y="Rank", size="Gene count", sizes=(100, 1000), hue="Z-score", palette="Reds", legend="brief")

        matplotlib.pyplot.grid(True)
        matplotlib.pyplot.yticks(down_enrichment_data["Rank"], down_enrichment_data["Term name"], fontsize="xx-small")
        matplotlib.pyplot.xlabel("-log10(Padj)")
        matplotlib.pyplot.ylabel(f"{len(down_enrichment_data)} pathways")
        matplotlib.pyplot.title(f"TNBC pathways in {background.replace('_', ' ')}")
        ax.invert_yaxis()

        matplotlib.pyplot.tight_layout()
        fig.savefig(f"{args.output}/{expression}-TNBC.pdf")
        fig.savefig(f"{args.output}/{expression}-TNBC.png")
        matplotlib.pyplot.close(fig)


if __name__ == "__main__":
    main()
