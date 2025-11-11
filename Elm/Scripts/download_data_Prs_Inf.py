# Need to load sratoolkit module before running this, should also probably make a conda environment realistically
import subprocess

accessions = ["SRR31567433", "SRR31567434", "SRR31567435", "SRR31567436", "SRR31567437", "SRR31567438", "SRR31567439", "SRR31567440"]

for acc in accessions:
    subprocess.run(["fastq-dump", "--split-files", "--gzip", acc])
