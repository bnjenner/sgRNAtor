#!/bin/bash

art=/restricted/projectnb/challenge2025/software/ART/art_src_MountRainier_Linux/art_illumina



# for ss, HiSeqX TruSeq: does 150bp paired end reads

$art -ss HSXt -i /restricted/projectnb/challenge2025/Data/apl_simdata/uniform_illumina_weighted/weighted_syn_sgRNAs.fa -o /restricted/projectnb/challenge2025/Data/apl_simdata/uniform_illumina_weighted/sim_data/uniform_sim_data -l 150 -f 20 -p -m 500 -s 10 -sam 
