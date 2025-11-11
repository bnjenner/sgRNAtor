import pandas as pd
genomepath = "/restricted/projectnb/challenge2025/Data/MN908947.3/MN908947.3.fasta"

with open(genomepath, "r") as genomefile:
    genome = genomefile.readlines()

genomstring = ""
for i in genome:
    if i[0] != ">":
        genomstring += i.strip("\n")

#print(genomstring)

leader_index = 70
leader_TRS = "acgaac"

orf_s = 21555 # one before num in bench
orf_3a = 25384
orf_e = 26236
orf_m = 26472

orf_6_notrs = 27201

orf_7a = 27387

orf_7b_possible = 27673

orf_8 = 27887
orf_n = 28259
orf_10_notrs = 29557

#print(genomstring[orf_10_notrs:])

all_fragments = [orf_s, orf_3a, orf_e, orf_m, orf_6_notrs, orf_7a, orf_7b_possible, orf_8, orf_n, orf_10_notrs]
orf_names = ["s", "3a", "e", "m", "6", "7a", "7b", "8", "n", "10"]

sgRNA_dicti = {}
for ind in range(len(all_fragments)):
    if ind not in [4, 9]:
        sgRNA = genomstring[:leader_index] + genomstring[all_fragments[ind]:]
    else:
        sgRNA = genomstring[:leader_index] + leader_TRS + genomstring[all_fragments[ind]:]
        print(sgRNA)
    sgRNA_dicti[orf_names[ind]] = sgRNA

    print(len(sgRNA))

sgrna_df = pd.DataFrame.from_dict(sgRNA_dicti, orient="index")
sgrna_df.to_csv("synthetic_sgRNAs.csv")
