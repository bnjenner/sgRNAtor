import os
import pandas as pd

simdatapath = "/restricted/projectnb/challenge2025/Data/apl_simdata/uniform_illumina_sim/sim_data/"
outpath = "/restricted/projectnb/challenge2025/Data/apl_simdata/uniform_illumina_sim/conc_sim_data/"

filetypes = ["fa.sam", "fa1.aln", "fa1.fq", "fa2.aln", "fa2.fq"]

for i in filetypes:
    with open(outpath + "conc_sim_data_" + i, "w") as outfile:
        for simfile in os.listdir(simdatapath):
            if i in simfile:
                print(simfile)
                with open(simdatapath + simfile, "r") as file:
                    lines = file.readlines()

                    # conditions to putting the files together

                    if i == filetypes[0]: #sam
                        for l in lines:
                            if l[0] != "@":
                                outfile.write(l)
                    elif i == filetypes[1] or i == filetypes[3]: #aln
                        for l in lines:
                            if l[0] != "#" and l[0] != "@":
                                outfile.write(l)
                    elif i == filetypes[2] or i == filetypes[4]: #fq
                        for l in lines:
                            outfile.write(l)






"""
with open("uniform_conc_1.fq" as ):
    for simfile in os.listdir(simdatapath):
        print("hi")
        with open(simfile, "r") as file:
            reads = file.readlines()

### taking a pause on this idea
"""