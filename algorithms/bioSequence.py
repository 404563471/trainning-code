
# 统计参考基因组中STR的位置和对应碱基单位和个数。
# 要求STR碱基为1-4bp,连续个数超过5次的输出。
# 例如chr1，10589，AT,10指从chr1的10589及之后有10个连续的AT
from Bio import SeqIO
import itertools

def search(sequence, target):
    seq_num=len(sequence)
    tar_num=len(target)
    seq_list=[]
    for i in range(seq_num):
        if target == sequence[i:i+tar_num]:
            seq_list.append(i) 
    return seq_list

def merge(seq_list, target, sequence, limit=5):
    '''
    类似处理等差序列的思路
    '''
    start=seq_list[0]
    merge_list=[]
    count=1
    for j in range(1, len(seq_list)):
        if seq_list[j] - seq_list[j-1] == len(target) :
            count += 1
        else :
            if count >= limit :
                merge_list.append([sequence.id, start, target, count])
            count=1
            start=seq_list[j]
    return merge_list
            
def tar_str(n=4):
    target_list=["A", "T", "C", "G"]
    ignore_list=[i * j for i in target_list for j in range(2, n+1)]
    for i in range(2, n+1) :
        for j in set(list(itertools.permutations("ATCG",i)) + list(itertools.combinations_with_replacement("ATCG", i))) :
            target = "".join(j)
            if target not in ignore_list :
                target_list.append(target)
    return target_list

result_list=[]
target_list=tar_str(4)
reference_path = "reference.fa"
for sequence in SeqIO.parse(reference_path, "fasta"):
    for target in target_list :
        seq_list = search(sequence, target)
        result_list.append(merge(seq_list, target, sequence))


