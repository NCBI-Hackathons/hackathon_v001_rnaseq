#!/usr/bin/env python
import sys
import os
import re

print "I ran so far away"
print sys.argv

bamOutfolder = '/data/yoons3/ncbi_hackathon/BAM/bambino/'
#bamOutfn = '/data/yoons3/ncbi_hackathon/BAM/bambino/'
refFlatfn = '/data/yoons3/ncbi_hackathon/mapping2gene/refFlat.txt'
if len(sys.argv) >= 2:
    bamOutfolder = sys.argv[1]
    refFlatfn = sys.argv[2]
print 'bam', bamOutfolder
print 'ref', refFlatfn

myFiles = []
for fn in os.listdir(bamOutfolder):
    if fn.startswith("all"):
        print fn
        myFiles.append('%s%s' % (bamOutfolder,fn))

writedir = '/data/yoons3/ncbi_hackathon/mapping2gene/'
hitfn = '%shit.txt' % writedir
hitfh = open(hitfn, 'w')  
missfn = '%smiss.txt' % writedir
missfh = open(missfn, 'w') 

for fn in myFiles:
    print fn
    bamOutfh = open(fn, 'r')

    refFlatfh = open(refFlatfn, 'r') 

    
    seen={}
    annot={}
# parse the bam output file - need to rule out header in the file
# header = bamOutfh.readline()
    for line in bamOutfh:
        if line.startswith("Sample\tGroup\tChromosome\tPosition\tRead"):
            continue
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
        found_at = ''
        for snp_pos in all_snp_pos:
            if int(txStart) <= snp_pos <= int(txEnd):
                found = True
    	        found_at = snp_pos
                break

        #all_GSM823518.normal.SRR358994.bam.bambino
        m=re.search("all_(\w+)\.(\w+)\.(\w+)", fn)
        if m:
            gsmnum = m.group(1)
            tumornormal = m.group(2)
            srrnum = m.group(3)
            
        else:
            gsmnum = "?"
            tumornormal = "?"
            srrnum = "?"
        try:
            read, reference = annot[geneChr][found_at]
        except Exception, e:
            read, reference = 'Error %s' % geneChr, str(e)

        mycols = [
                gsmnum, 
                tumornormal, 
                srrnum, 
                geneName, 
                refName, 
                geneChr, 
                str(txStart), 
                str(txEnd), 
                str(found_at), 
                read, 
                reference]

        if found:
            print ' hit ', mycols
            
            hitfh.write('\t'.join(mycols))
            hitfh.write('\n')

        else:
            print ' no snp ', mycols
            missfh.write('\t'.join(mycols))
            missfh.write('\n')            

    
    
    
    
