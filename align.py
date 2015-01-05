"""
align.py

NCBI Hackathon, RNA-seq team
January 5, 2015
Created by Abhi Nellore

Aligns RNA-seq FASTQs specified by a manifest file, each of whose lines has the
following format:

SRA accession number <TAB> sample group <TAB> sample name

Outputs BAM files. Each filename is in the following format:

<sample name>.<sample group>.<original FASTQ name>.bam

Dependencies: HISAT, fastq-dump from sra-toolkit, samtools
"""
import multiprocessing

def download_and_align_data(sra_accession, bam_filename,
							fastq_dump_exe='fastq-dump', hisat_exe='hisat',
							hisat_args='', samtools_exe='samtools',
							num_threads=4):
	""" Uses fastq-dump to download sample FASTQ(s) and aligns it with HISAT.

		sra_accession: sample accession number on SRA
		bam_filename: full path to BAM filename
		fastq_dump_exe: path to fastq-dump executable
		hisat_exe: path to HISAT executable
		num_threads: argument of HISAT's -p parameter
		hisat_args: supplementary arguments to pass to HISAT; these follow
			the -p parameter specified by num_threads and thus can override it
		samtools_exe: path to SAMTools executable

		Return value: None if successful and error message if unsuccessful
	"""
	

if __name__ == '__main__':
	import argparse
	# Print file's docstring if -h is invoked
    parser = argparse.ArgumentParser(description=__doc__, 
                formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--manifest', '-m', type=str, required=True,
    						help='path to manifest file')
    parser.add_argument('--hisat-exe', type=str, required=False,
    						default='hisat',
    						help='path to HISAT executable')
    parser.add_argument('--hisat-args', type=str, required=False,
    						default='',
    						help='supplementary arguments to pass to HISAT')
    parser.add_argument('--fastq-dump-exe', type=str, required=False,
    						default='fastq-dump',
    						help='path to fastq-dump executable')
    parser.add_argument('--samtools-exe', type=str, required=False,
    						default='samtools',
    						help='path to SAMTools executable')
    parser.add_argument('--out', type=str, required=False,
    						default='./',
    						help='output directory')
    parser.add_argument('--num-processes', '-p', type=int, required=False,
    						default=4,
    						help=('number of simultaneous downloads/HISAT '
    							  'instances to run'))
    parser.add_argument('--num-threads', '-t', type=int, required=False,
    						default=4,
    						help=('number of cores allocated to each HISAT '
    							  'instance'))
    args = parser.parse_args()
