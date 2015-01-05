#!/usr/bin/env bash
# NCBI Hackathon, RNA-seq team
# January 5, 2015
# Created by Abhi Nellore
# Downloads and installs: HISAT 0.1.2-beta, HISAT index for hg19, SAMTools 1.1, Bambino, Illumina iGenome for UCSC hg19
set -e

# Set working directory here; make sure you have write access to it!
WORK=/blast/rna

cd $WORK
# Download HISAT
curl -O http://www.ccb.jhu.edu/software/hisat/downloads/hisat-0.1.2-beta-Linux_x86_64.zip || { echo "error downloading HISAT"; exit 1; }
unzip hisat-0.1.2-beta-Linux_x86_64.zip || { echo "error unzipping HISAT"; exit 1; }
sudo ln -s `pwd`/hisat-0.1.2-beta/hisat /usr/local/bin || { echo "hisat is already installed"; }
sudo ln -s `pwd`/hisat-0.1.2-beta/hisat-build /usr/local/bin || { echo "hisat-build is already installed"; }
# Download and make SAMTools
curl -OL http://downloads.sourceforge.net/project/samtools/samtools/1.1/samtools-1.1.tar.bz2 || { echo 'curl failed' ; exit 1; }
tar xvjf samtools-1.1.tar.bz2 || { echo "samtools untar+gunzip failed" ; exit 1; }
cd samtools-1.1
sudo make || { echo 'samtools make failed'; exit 1; }
# Download HISAT index
curl -OL ftp://ftp.ccb.jhu.edu/pub/data/hisat_indexes/hg19_hisat.tar.gz || { echo 'error downloading UCSC hg19 HISAT index'; exit 1; }
tar xvzf hg19_hisat.tar.gz|| { echo "HISAT index untar+gunzip failed"; exit 1; }
# Download hg19 iGenome
curl -OL ftp://igenome:G3nom3s4u@ussd-ftp.illumina.com/Homo_sapiens/UCSC/hg19/Homo_sapiens_UCSC_hg19.tar.gz
tar xvzf Homo_sapiens_UCSC_hg19.tar.gz || { echo "iGenomes untar+gunzip failed"; exit 1; }
# Download and install Bambino
cd ..
curl -o bambino.jar -OL https://cgwb.nci.nih.gov/cgi-bin/bambino?download_bambino_jar=bundle || { echo 'curl failed' ; exit 1; }
# Download and install sra-toolkit
curl -OL http://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/2.4.2-4/sratoolkit.2.4.2-ubuntu64.tar.gz || { echo 'curl failed' ; exit 1; }
tar xvzf sratoolkit.2.4.2-ubuntu64.tar.gz || { echo "sratoolkit untar+gunzip failed"; exit 1; }
sudo ln -s `pwd`/sratoolkit.2.4.2-ubuntu64/bin/fastq-dump /usr/local/bin || { echo "fastq-dump is already installed"; }