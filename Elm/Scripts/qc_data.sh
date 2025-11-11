#!/bin/bash -l
#$ -P challenge2025          # Specify the SCC project name you want to use
#$ -l h_rt=99:59:00
#$ -N fastqc         # Give job a name
#$ -o logs/QC
#$ -e logs/QC
#$ -m bea

start=`date +%s`
echo $HOSTNAME

sra_id="PRJNA1193019"
outpath="../../../Data/QC/${sra_id}"
inpath="../../${sra_id}"


mkdir -p ${outpath}
cd ${outpath}

module load fastqc/0.12.1
module load multiqc/1.12

for i in ${inpath}/*.fastq.gz
do
		echo $i
        fastqc -o ${outpath} $i
done

multiqc .