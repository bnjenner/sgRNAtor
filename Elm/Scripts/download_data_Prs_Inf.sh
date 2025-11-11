#!/bin/bash -l
#PBS -P challenge2025
#PBS -N download_data

module load sratoolkit
module load python3

python3 ../../Elm/Scripts/download_data_Prs_Inf.py
