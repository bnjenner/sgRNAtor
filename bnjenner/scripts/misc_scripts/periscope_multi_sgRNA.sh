#!/bin/bash -l
#$ -l h_rt=24:00:00
#$ -P challenge2025
#$ -N periscope_multi
#$ -t 1-11
#$ -pe omp 8
#$ -o logs/classify
#$ -e logs/classify
#$ -m bea

start=`date +%s`
echo $HOSTNAME
echo "My SGE_TASK_ID: " $SGE_TASK_ID

threads=${OMP_NUM_THREADS}
sample=`sed "${SGE_TASK_ID}q;d" samples_PRJNA726840.txt`
echo "SAMPLE: ${sample}"

# Set / Create Directories
export baseP=/restricted/projectnb/challenge2025/sgRNAtor/bnjenner
export cwd=${baseP}/scripts
export seqP=${baseP}/00-RawData
export outP=${baseP}/01-PeriscopeMulti_sgRNA/${sample}
export refP=/restricted/projectnb/challenge2025/software/periscope_multifasta/periscope_multi/resources
export tmpP=${cwd}/tmp

[[ -d ${outP} ]] || mkdir -p ${outP}
[[ -d ${tmpP} ]] || mkdir -p ${tmpP}


module load miniconda/24.5.0
conda activate /restricted/projectnb/challenge2025/software/conda_envs/periscope_multifasta/

# Gunzip because BWA sucks
gunzip -c ${seqP}/${sample}_1.fastq.gz > ${cwd}/tmp/${sample}_1.fastq
gunzip -c ${seqP}/${sample}_2.fastq.gz > ${cwd}/tmp/${sample}_2.fastq

# Periscope Multi Identify sgRNA
call="periscope_multi \
        --fastq ${cwd}/tmp/${sample}_1.fastq ${cwd}/tmp/${sample}_2.fastq \
	--sample ${sample} --output-prefix ${outP}/${sample} \
        --artic-primers V3 --resources ${refP} --gff ${refP}/covid.gff \
        --technology illumina --threads  ${threads}"
echo $call
eval $call

# Clean up
#rm -rf ${cwd}/tmp/${sample}_*

end=`date +%s`
runtime=$((end-start))
echo $runtime
