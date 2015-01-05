#!/usr/bin/env bash

set -e

cd /blast
mkdir -p work || { echo "cannot create work directory in /blast"; exit 1; }
cd work
# Download HISAT
curl -O http://www.ccb.jhu.edu/software/hisat/downloads/hisat-0.1.2-beta-Linux_x86_64.zip || { echo "error downloading HISAT"; exit 1; }
unzip hisat-0.1.2-beta-Linux_x86_64.zip || { echo "error unzipping HISAT"; exit 1; }
sudo ln -s `pwd`/hisat-0.1.2-beta-Linux_x86_64/hisat /usr/local/
sudo ln -s `pwd`/hisat-0.1.2-beta-Linux_x86_64/hisat-build /usr/local/bin
# Download and make SAMTools
sudo yum -y install ncurses-devel ncurses || { echo "curses installation failed" ; exit 1; }
curl -O http://downloads.sourceforge.net/project/samtools/samtools/1.1/samtools-1.1.tar.bz2 || { echo 'curl failed' ; exit 1; }
tar xvjf samtools-1.1.tar.bz2 || { echo "samtools untar+gunzip failed" ; exit 1; }
cd samtools-1.1
sudo make || { echo 'samtools make failed'; exit 1; }
cd ..
sudo ln -s `pwd`/samtools-0.1.19/samtools /usr/local/bin
# Download and install Bambino
curl -OL https://cgwb.nci.nih.gov/cgi-bin/bambino?download_bambino_jar=bundle || { echo 'curl failed' ; exit 1; }