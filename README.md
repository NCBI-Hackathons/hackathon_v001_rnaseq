# Variant calling for RNA-seq @ NCBI Hackathon
## January 5-7, 2015

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/DCGenomics/hackathon_v001_rnaseq?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

This RNA-seq analysis pipeline measures the frequency of each type of substitution (e.g., A->G) in each of a set of human RNA-seq samples on the [Sequence Read Archive](http://www.ncbi.nlm.nih.gov/sra). The samples, specified in a manifest file, are divided into two groups. The pipeline looks for a statistically significant differences in frequencies of substitutions between the two groups via ??????. Every line of the manifest file is either a comment (denoted by an initial # character) or three tab-separated fields:
```
SRA run accession number <TAB> sample group <TAB> sample name
```
A run accession number always begins with "SRR". The pipeline assumes that there are exactly two sample groups, e.g., "tumor" or "normal." Both sample group and sample name should contain no spaces.

The pipeline has several dependencies:

1. [HISAT](http://www.ccb.jhu.edu/software/hisat/index.shtml), a fast spliced alignment tool.
2. HISAT index for UCSC hg19 (ftp://ftp.ccb.jhu.edu/pub/data/hisat_indexes/hg19_hisat.tar.gz), a hierarchical FM index required by HISAT.
3. [Bambino](https://cgwb.nci.nih.gov/goldenPath/bamview/documentation/index.html), a variant caller that pools data from multiple input files.
4. [UCSC hg19 Illumina iGenome](http://support.illumina.com/sequencing/sequencing_software/igenome.html), whose genome annotation `genes.gtf` is used to provide a list of known introns to HISAT.
5. [SAMTools](http://samtools.sourceforge.net/) for conversion to sorted, indexed BAM and mpileup.
6. [SRA Toolkit](http://www.ncbi.nlm.nih.gov/sites/books/NBK158900/) for downloading SRAs and converting them to raw FASTQs.

To install these dependencies on an Amazon EC2 instance running Ubuntu, enter
```
sh ec2_bootstrap.sh WORK
```
where WORK is a work directory on the instance with at least ~three times as much space as the sample FASTQs demand.
The pipeline is run as follows.

a) Download and align data with align.py. Command-line parameters can be viewed by running
```
python align.py --help
```
An example alignment command run by the hackathon team is
```
python align.py -m /blast/rna/hackathon_v001_rnaseq/testset.txt
--hisat-idx /blast/rna/hg19_hisat/hg19_hisat
--gtf /blast/rna/Homo_sapiens/UCSC/hg19/Annotation/Genes/genes.gtf
--out /blast/rna/aligned/
--fastq-dump-exe /blast/rna/sratoolkit.2.4.2-ubuntu64/bin/fastq-dump
--num-processes 6 --gzip-output --temp /blast/rna/temp
--hisat-args "--trim3 10" 2>/blast/rna/hackathon_v001_rnaseq/6.log
```
Note that the manifest file described above is specified with the `-m` parameter.

b) Run prepare_bam.pl to process the alignment files (SAM), remove the unmapped, low-quality or ambiguous reads (e.g. reads that map at multiple different locations). Command-line parameters can be viewed by running the script without parameters
```
perl prepare_bam.pl
```
An example command is
```
perl prepare_bam.pl -v /blast/rna/aligned/GSM823518.normal.SRR358994.sam.gz /blast/rna/BAM/output/
```
c) Run run_bambino.pl to generate the variant call table. Each line of the output contains a call variant at a particular location within the genome and the reference base at the same location. Command-line parameters can be viewed by running the script without parameters
```
perl run_bambino.pl
```
An example command is
```
perl run_bambino.pl /blast/rna/BAM/output/chr1_GSM823518.normal.bam /blast/rna/BAM/output/chr1_GSM823518.normal.bambino
```
d) Before start to map bambino output chromosome location to refGene, you need to download refFlat.txt(from UCSC http://hgdownload.soe.ucsc.edu/goldenPath/hg19/database/). Then, download and run mapping2gene.py. Inside the result file, header is "Gene name <TAB> refGene name <TAB> Chromosome <TAB> Transcription start <TAB> Transcription end <TAB> Variant found at <TAB> Alternate base <TAB> Reference base".

An example command is
```
python mapping2gene.py /absolute/path/to/output/file(from run_bambino) /absolute/path/to/refFlat.txt
```
   This will produce hit.txt and miss.txt. hit.txt has candidate variant info. which mapped to inside the trascription region  of the gene. This process also makes count_mapping2gene.txt, which is a statistical table for every transition(A>C, A>G ,and etc) in each samples.


