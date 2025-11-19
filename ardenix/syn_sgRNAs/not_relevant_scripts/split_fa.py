
synsgrnapath = "/restricted/projectnb/challenge2025/sgRNAtor/ardenix/syn_sgRNAs/syn_sgRNAs.fa"
orf_names = ["s", "3a", "e", "m", "6", "7a", "7b", "8", "n", "10"]


with open(synsgrnapath, "r") as file:
    syn_file = file.readlines()

seqlist = []
for i in syn_file:
    if i[0] != ">":
        seqlist.append(i)

for i in range(len(orf_names)):

    with open(orf_names[i] + "_syn_sgrna.fa", 'a') as file_object:
        file_object.write("> " + orf_names[i] + "\n")
        file_object.write(seqlist[i])
        file_object.close()