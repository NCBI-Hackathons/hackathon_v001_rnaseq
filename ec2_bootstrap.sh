#!/usr/bin/env bash

# Set working directory here; make sure you have write access to it!
WORK=/blast/rna

set -e

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
# Download and install Bambino
cd ..
curl -OL https://cgwb.nci.nih.gov/cgi-bin/bambino?download_bambino_jar=bundle || { echo 'curl failed' ; exit 1; }