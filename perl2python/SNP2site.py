import os
import pandas as pd
inputfile="example/G1.vcf"
outputdir="snp_stat"
windows=100000
fastaIndex="example/hg19.fa.fai"
#NAME	Name of this reference sequence
#LENGTH	Total length of this reference sequence, in bases
#OFFSET	Offset in the FASTA/FASTQ file of this sequence's first base
#LINEBASES	The number of bases on each line
#LINEWIDTH	The number of bytes in each line, including the newline
#QUALOFFSET	Offset of sequence's first quality within the FASTQ file

if not os.path.exists(outputdir):
    os.makedirs(outputdir+"/data")
    os.makedirs(outputdir+"/conf")
else:
    print(outputdir, " is existed")

chroms=["chr"+str(i) for i in range(1,24)]

refInfo=pd.read_csv(fastaIndex, sep="\t", header=None)
refInfo.Index
print(refInfo)

