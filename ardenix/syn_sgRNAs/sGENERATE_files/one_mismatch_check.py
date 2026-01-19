import pandas as pd
import matplotlib.pyplot as plt

path = "/restricted/projectnb/challenge2025/sgRNAtor/ardenix/syn_sgRNAs/genome/genome.fa"

#trs = "acgaac"
trs = "ACGAAC"

genome_string = ""
with open(path, "r") as p:
    reader = p.readlines()
    for line in reader:
        if line[0] != ">":
            genome_string += line.strip("\n")

print(genome_string)

matching_indices = []
one_mismatch_indices = []

guide = 0
while guide < (len(genome_string) - len(trs)):
    check = genome_string[guide:guide+len(trs)]


    if check == trs:
        matching_indices.append(guide)
        print(guide)

    else:
        catch = 0
        for i in range(len(trs)):
            if check[i] != trs[i]:
                catch+=1
        
        if catch == 1:
            one_mismatch_indices.append(guide)
    
    guide +=1

print("perfect match TRSs")
print(matching_indices)
print(len(matching_indices))
print(" ")
print("one mismatch with TRSs")
print(one_mismatch_indices)
print(len(one_mismatch_indices))

fig = plt.figure(figsize=(8, 6))
plt.hist(one_mismatch_indices, bins=20)
plt.xlabel("Location in Genome (30kb)")
plt.ylabel("Frequency of Sequence Found")
plt.title("Histogram of Sites with One Mismatch from TRS (20 Bins)")
plt.savefig("one_mismatch_check_in_genome_20bins.png")
y = []
for i in range(len(one_mismatch_indices)):
    y.append(0)

fig = plt.figure(figsize=(8, 6))
plt.scatter(one_mismatch_indices, y, s=10)
plt.xlabel("Location in Genome (30kb)")
plt.title("Distribution of Sites with One Mismatch from TRS")
#plt.savefig("one_mismatch_as_line.png")