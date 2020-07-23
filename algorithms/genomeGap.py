from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from collections import defaultdict


def bedPositions(bed_path):
    positions = defaultdict(list)
    with open(bed_path) as f:
        for line in f:
            name, start, stop = line.split()
            positions[name].append((int(start), int(stop)))
    return positions


def telomere(positions, repeat="taaccc"):
    global records
    for name in positions:
        target_seq_record = records[name]
        target_seq = target_seq_record.seq.tomutable()
        for (start, stop) in positions[name]:
            target_seq[start:stop] = repeat * int((stop-start)/len(repeat))
        records[name].seq = target_seq.toseq()

def dict2records(records):
    for record in records.values():
        yield record

def targetSeq(records, positions):
    target_seqs=[]
    for name in positions:
        for (start, stop) in positions[name]:
            target_seqs.append(records[name][start:stop])
    return target_seqs


def centromere(positions, tarSeqs):
    global records
    for name in positions:
        target_seq_record = records[name]
        target_seq = target_seq_record.seq.tomutable()
        for (start, stop) in positions[name]:
            target_seq[start:stop] = tarSeqs[name].seq
        records[name].seq = target_seq.toseq()



records= SeqIO.to_dict(SeqIO.parse(open('ref/hg19.fa'), 'fasta'))
telomerePositions = bedPositions("ref/telomere.bed")
telomere(telomerePositions)
#SeqIO.write(telomereRecords, "ref/hg19_telomere.fa", "fasta")
#hg38Posi = bedPositions("hg38centromere.txt")
#hg38Raw = SeqIO.to_dict(SeqIO.parse(open('ref/hg38.fa'), 'fasta'))
#centromereRecord = targetSeq(hg38Raw, hg38Posi)
#SeqIO.write(centromereRecord, "ref/centromere.fa", "fasta")

#hg19Tel = SeqIO.to_dict(SeqIO.parse(open('ref/hg19_telomere.fa'), 'fasta'))
centromereRecord = SeqIO.to_dict(SeqIO.parse(open('ref/centromere.fa'), 'fasta'))
hg19CentroPositions = bedPositions("hg19centromere.txt")
centromere(hg19CentroPositions, centromereRecord)

SeqIO.write(dict2records(records), "ref/hg19_centromere.fa", "fasta")
