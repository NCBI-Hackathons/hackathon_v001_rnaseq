#!/usr/bin/env python
import sys

bamOutfn = '/blast/rna/mapping2gene/bambino.output'
refFlatfn = '/blast/rna/mapping2gene/refFlat.txt'
if len(sys.argv) >= 2:
    bamOutfn = sys.argv[1]
    refFlatfn = sys.argv[2]
#print 'bam', bamOutfn
#print 'ref', refFlatfn

bamOutfh = open(bamOutfn, 'r')
refFlatfh = open(refFlatfn, 'r') 

hitfn = '/blast/rna/mapping2gene/hit.txt'
hitfh = open(hitfn, 'w')  
missfn = '/blast/rna/mapping2gene/miss.txt'
missfh = open(missfn, 'w') 
  
seen={}
annot={}
# parse the bam output file - need to rule out header in the file
header = bamOutfh.readline()
for line in bamOutfh:
    seqLoc = line.split('\t')
    sample = seqLoc[0]
    group = seqLoc[1]
    chr = seqLoc[2]
    loc = int(seqLoc[3])
    read = seqLoc[4]
    reference = seqLoc[5]
    if chr not in seen:
        seen[chr] = []
	annot[chr] = {}

    seen[chr].append(loc)
    annot[chr][loc] = read, reference

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
    found_at = None
    for snp_pos in all_snp_pos:
        if int(txStart) <= snp_pos <= int(txEnd):
            found = True
	    found_at = snp_pos
            break

    if found:
	#read, reference = annot[geneChr][found_at]
        try:
            read, reference = annot[geneChr][found_at]
        except Exception, e:
            read, reference = 'Error %s' % geneChr, str(e)
        print ' hit ', geneName, refName, geneChr, txStart, txEnd, found_at, read, reference
        hitfh.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (geneName, refName, geneChr, txStart, txEnd, found_at, read, reference))
    else:
        #read, reference = annot[geneChr][found_at]
        try:
            read, reference = annot[geneChr][found_at]
        except Exception, e:
            read, reference = 'Error %s' % geneChr, str(e)
        print ' no snp ', geneName, refName, geneChr, txStart, txEnd, found_at, read, reference
        missfh.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (geneName, refName, geneChr, txStart, txEnd, found_at, read, reference))
        #print 'no snp', geneName, refName, geneChr, txStart, txEnd
        #missfh.write('%s\t%s\t%s\t%s\t%s\n' % (geneName, refName, geneChr, txStart, txEnd))



