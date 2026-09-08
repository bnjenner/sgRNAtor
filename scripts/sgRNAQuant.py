import os
import argparse
from sgRNAtor import quantify
from sgRNAtor import stats
from sgRNAtor import utils

#################################################
# Argparser
def argparser():
	parser = argparse.ArgumentParser(description="Quantify sgRNAs from an already-aligned BAM. Identifies template switching sites and assigns them to ORFs, skipping the leader search and alignment stages of the main sgRNAtor pipeline.")
	parser.add_argument("bam", help="Aligned BAM file.")
	parser.add_argument("--tss-bed", "-b", type=str, default=utils.bundled("sgRNA_template_switch_sites.bed"), help="Path to sgRNA template switching sites bed file. (default: bundled SARS-CoV-2 junctions)")
	parser.add_argument("--tss-window", "-w", type=int, default=10, help="Window size for template switching sites (+/- specified number). (default: 10)")
	parser.add_argument("--output-prefix", "-o", type=str, default="sgRNAtor_result", help="Prefix for output files.")
	args = parser.parse_args()

	# Check Input Files
	if not os.path.isfile(args.bam):
		raise RuntimeError(f"// ERROR: Bam ({args.bam}) does not exist")

	# TSS BedFile
	if not os.path.isfile(args.tss_bed):
		raise RuntimeError(f"// ERROR: Bed ({args.tss_bed}) does not exist")

	# TSS Window
	if args.tss_window < 0:
		raise RuntimeError(f"// ERROR: Please use a valid window size.")

	return args


#################################################
# Main
def main():

	args = argparser()

	orfs_tsv = f"{args.output_prefix}_ORF_counts.txt"
	sgrnas_tsv = f"{args.output_prefix}_sgRNA_counts.txt"
	summary_tsv = f"{args.output_prefix}_summary.txt"

	print("// Beginning sgRNA Quantification")
	quant = quantify.sgRNAquantify(bam = args.bam)
	quant.find_template_switches()
	quant.assign_TSS_to_orfs(tss_bed = args.tss_bed, window = args.tss_window)

	# Counts and CPMs live on sgRNAstats, not sgRNAquantify. Without the search
	# stage there is no raw library size, so CPMs are normalized to the aligned
	# fragments present in the BAM.
	summary = stats.sgRNAstats(sample = args.output_prefix)
	summary.library_size      = quant.stat_counts["aligned_fragments"]
	summary.aligned_fragments = quant.stat_counts["aligned_fragments"]
	summary.canonical         = quant.stat_counts["canonical"]
	summary.noncanonical      = quant.stat_counts["noncanonical"]
	summary.tss_dict          = quant.tss_dict
	summary.sgRNA_counts      = quant.sgRNA_counts
	summary.unassigned        = quant.unassigned

	summary.write_ORF_counts(output_file = orfs_tsv)
	summary.write_sgRNA_counts(output_file = sgrnas_tsv)
	summary.write_summary(output_file = summary_tsv)
	print(f"// sgRNAtor Quantification Complete.")


#################################################
if __name__ == "__main__":
	main()
