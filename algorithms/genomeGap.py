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


def telomere(records, positions, repeat="taaccc"):
    target_seq_records = []
    for name in positions:
        target_seq_record = records[name]
        target_seq = target_seq_record.seq.tomutable()
        for (start, stop) in positions[name]:
            target_seq[start:stop] = repeat * int((stop-start)/len(repeat))
        target_seq_record = SeqRecord(target_seq, id=name, description='')
        target_seq_records.append(target_seq_record)
    return target_seq_records


rawRecords = SeqIO.to_dict(SeqIO.parse(open('ref/hg19.fa'), 'fasta'))
telomerePositions = bedPositions("ref/telomere.bed")
telomereRecords = telomere(rawRecords, telomerePositions)
SeqIO.write(telomereRecords, "ref/hg19_telomere.fa", "fasta")
