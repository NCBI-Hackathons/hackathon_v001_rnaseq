#!/usr/bin/env python
import sys

bamOutfn = '/Users/yoons3/mapping2gene/output_test.tab'
refFlatfn = '/Users/yoons3/mapping2gene/refFlat.txt'
if len(sys.argv) >= 2:
    bamOutfn = sys.argv[1]
    refFlatfn = sys.argv[2]
#print 'bam', bamOutfn
#print 'ref', refFlatfn

bamOutfh = open(bamOutfn, 'r')
refFlatfh = open(refFlatfn, 'r') 

hitfn = 'hit.txt'
hitfh = open(hitfn, 'w')  
missfn = 'miss.txt'
missfh = open(missfn, 'w') 
  
seen={}
# parse the bam output file - need to rule out header in the file
header = bamOutfh.readline()
for line in bamOutfh:
    seqLoc = line.split('\t')
    chr = seqLoc[3]
    loc = int(seqLoc[4])
    if chr not in seen:
        seen[chr] = []
    seen[chr].append(loc)

# parse the ref file
for line in refFlatfh:
    geneLoc = line.split('\t')
    geneName = geneLoc[0]
    refName = geneLoc[1]
    geneChr = geneLoc[2]
    txStart = geneLoc[4]
    txEnd = geneLoc[5]

    if geneChr in seen:
        all_snp_pos = seen[geneChr]
    else:
        all_snp_pos = []

    found = False
    for snp_pos in all_snp_pos:
        if int(txStart) <= snp_pos <= int(txEnd):
            found = True
            break

    if found:
        print ' hit ', geneName, refName, geneChr, txStart, txEnd
        hitfh.write('%s\t%s\t%s\t%s\t%s\n' % (geneName, refName, geneChr, txStart, txEnd))
    else:
        print 'no snp', geneName, refName, geneChr, txStart, txEnd
        missfh.write('%s\t%s\t%s\t%s\t%s\n' % (geneName, refName, geneChr, txStart, txEnd))




