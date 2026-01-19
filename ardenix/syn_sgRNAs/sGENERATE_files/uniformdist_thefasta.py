import pandas as pd
import matplotlib.pyplot as plt

path3 = "/restricted/projectnb/challenge2025/sgRNAtor/ardenix/syn_sgRNAs/sGENERATE_files/sgRNAs_only.faa"
path4 = "/restricted/projectnb/challenge2025/sgRNAtor/ardenix/syn_sgRNAs/sGENERATE_files/sgRNAs_only_uniform30x.faa"

path = "/restricted/projectnb/challenge2025/sgRNAtor/ardenix/syn_sgRNAs/sGENERATE_files/COV_multifastq_nc.faa"
path2 = "/restricted/projectnb/challenge2025/sgRNAtor/ardenix/syn_sgRNAs/sGENERATE_files/COV_multifastq_nc_uniform10x.faa"

genome_string = ""
with open(path3, "r") as p:
    with open(path4, "w") as out1:
        reader = p.readlines()
        for line_num in range(len(reader)):
            name = reader[line_num]
            if name[0] == ">":
                sequence = reader[line_num+1]
                nm = name.strip("\n")
                if "\n" in sequence:
                    seq = sequence.strip("\n")
                else:
                    seq = sequence
                for i in range(30):
                    out1.write(nm + "_" + str(i) + "\n")
                    out1.write(seq + "\n")
                