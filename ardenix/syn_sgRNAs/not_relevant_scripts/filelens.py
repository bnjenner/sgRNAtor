import pandas as pd
import matplotlib.pyplot as plt

filename = "/restricted/project/challenge2025/Data/PRJNA603194/SRR10971381.fastq"

#lens = []

lensdict = {}

maxlen = 0

with open(filename, 'r') as file:
    for line in file:
        if "length" in line:
            length = line.split("=")[1]
            length = int(length)

            if length > maxlen:
                maxlen = length
            if length not in lensdict.keys():
                lensdict[length] = 1
            else:
                lensdict[length] +=1

    #lens.sort()
    #print(lensdict)
    #print(maxlen)

lensitems = lensdict.items()
sorteditems = sorted(lensitems)
sortedlensdict = dict(sorteditems)
x = sortedlensdict.keys()
y = sortedlensdict.values()

y = list(y)
reads_shorter_than_300 = sum(y[:-5])
reads_300_or_301 = sum(y[-5:])
totalreads = sum(y)

print(reads_shorter_than_300)
print(reads_300_or_301)
print(totalreads)


#binwidth = 10
#leftedges = (x - binwidth) /2

#plt.hist(y, color="cornflowerblue")
#plt.savefig("SRR10971381_hist_of_lens.png")
#plt.show()

plt.plot(x,y, color="cornflowerblue")

plt.xlabel("Length of Read")
plt.ylabel("Frequency of Length of Read")
plt.title("Frequency of Lengths of Reads in SRR10971381.fastq")

plt.savefig("SRR10971381_plot_of_lens_freqs.png")








