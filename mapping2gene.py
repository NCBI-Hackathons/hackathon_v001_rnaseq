#!/usr/bin/env python

bamOutfn = '/Users/yoons3/mapping2gene/output_test.tab'
bamOutfh = open(bamOutfn, 'r')
refFlatfn = '/Users/yoons3/mapping2gene/refFlat.txt'
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
    print '::1::',chr, loc
    if chr not in seen:
        seen[chr] = []
    seen[chr].append(loc)
#import pdb
#pdb.set_trace()


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
        found = False
        for snp_pos in all_snp_pos:
            if int(txStart) <= snp_pos <= int(txEnd):
                found = True
                break
                #print ' hit ', geneName, refName, geneChr, txStart, txEnd
            else:
                pass
                #print ' miss ', geneName, refName, geneChr, txStart, txEnd
        if found:
             print ' hit ', geneName, refName, geneChr, txStart, txEnd

    else:
        pass
#        print 'no', geneName, refName, geneChr, txStart, txEnd
#    print '  2  ', geneName, refName, geneChr, txStart, txEnd


