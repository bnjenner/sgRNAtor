#!/bin/bash -l

# this is an attempt at QC-ing my data
# taken from Elm's qc_data_incl_htstream.sh

#$ -l h_rt=12:00:00
#$ -P challenge2025
#$ -N htstream
#$ -t 1
#$ -pe omp 8
#$ -o logs/QC/prepro
#$ -e logs/QC/prepro
#$ -m bea

start=`date +%s`
echo $HOSTNAME
echo "My SGE_TASK_ID: " $SGE_TASK_ID

proj="sim_data"
s=`sed "${SGE_TASK_ID}q;d" sim_data.txt`
echo "SAMPLE: ${sample}"

# Set / Create Directories
export baseP=/restricted/projectnb/challenge2025/sgRNAtor/ardenix/syn_sgRNAs
export cwd=${baseP}/bash_scripts
#export seqP=/restricted/projectnb/challenge2025/Data/${proj}
export seqP=/restricted/projectnb/challenge2025/Data/apl_simdata/uniform_illumina_weighted/${proj}
# /restricted/projectnb/challenge2025/Data/apl_simdata/uniform_illumina_sim/conc_sim_data
export outP=${baseP}/01-HTStream_prepro/${proj}
export qcP=${baseP}/02-MultiQC

[[ -d ${outP} ]] || mkdir -p ${outP}



# Module Loading
module load fastqc/0.12.1
module load miniconda/24.5.0
# HTStream Preprocessing
conda activate /restricted/projectnb/challenge2025/software/conda_envs/HTStream_v1.4.1
for sample in ${seqP}/*1.fq
do
s=${sample##*/}
s=${s%1.fq}
call="hts_Stats -L ${outP}/${s}.json -N 'initial stats' \
          -1 ${seqP}/${s}1.fq -2 ${seqP}/${s}2.fq | \
          -r -s ${rrna} | \
      hts_AdapterTrimmer -A ${outP}/${s}.json -N 'trim adapters' | \
      hts_QWindowTrim -A ${outP}/${s}.json -N 'quality trim the ends of reads' | \
      hts_NTrimmer -A ${outP}/${s}.json -N 'remove any remaining N bases' | \
      hts_LengthFilter -A ${outP}/${s}.json -N 'remove reads < 30 bp' \
          -n -m 30 | \
      hts_Stats -A ${outP}/${s}.json -N 'final stats' \
          -f ${outP}/${s}"
echo $call
eval $call


# Additional QC with fastqc
call="fastqc ${outP}/${s}*.fq \
       --outdir ${outP} \
       --dir ${outP}"
echo $call
eval $call
done

# Create MultiQC Report
call="multiqc -i multiqc_${proj} \
	-o ${qcP} -f ${outP}"
echo $call
eval $call

end=`date +%s`
runtime=$((end-start))
echo $runtime
