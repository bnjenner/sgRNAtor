# inspired by Elm
# need to do module load sratoolkit
# this is for PRJNA03194
# i genuinely think it only has one run in it

import subprocess

accessions = ["SRR10971381"]

for acc in accessions:
    subprocess.run(["fastq-dump", acc])
