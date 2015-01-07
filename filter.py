"""
filter.py

NCBI Hackathon, RNA-seq team
January 7, 2015
Created by Abhi Nellore

Filters out all read (pairs) for which there is at least one secondary
alignment. This is a dirty way to simulate filtering out all reads for which
NH:i > 1; this field is missing from HISAT output.
"""
import sys

if __name__ == '__main__':
    line = sys.stdin.readline()
    while line[0] == '@':
        sys.stdout.write(line)
        line = sys.stdin.readline()
    alignments = []
    tokens = line.strip().split('\t')
    last_read = tokens[0]
    alignments.append(tokens)
    while line:
        tokens = line.strip().split('\t')
        if tokens[0] != last_read:
            if not any([int(fields[1]) & 256 for fields in alignments]):
                for fields in alignments:
                    print '\t'.join(fields)
            alignments = []
        alignments.append(tokens)
    if alignments:
        if not any([int(fields[1]) & 256 for fields in alignments]):
            for fields in alignments:
                print '\t'.join(fields)