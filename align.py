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
import subprocess
import tempfile
import atexit
import os
import shutil

def download_and_align_data(sra_accession, bam_filename, hisat_idx, temp_dir,
                            fastq_dump_exe='fastq-dump', hisat_exe='hisat',
                            hisat_args='', samtools_exe='samtools',
                            num_threads=4):
    """ Uses fastq-dump to download sample FASTQ(s) and aligns data with HISAT.

        sra_accession: sample accession number on SRA
        bam_filename: full path to BAM filename
        hisat_idx: full path to HISAT index basename
        temp_dir: temporary directory for storing downloaded fastqs
        fastq_dump_exe: path to fastq-dump executable
        hisat_exe: path to HISAT executable
        num_threads: argument of HISAT's -p parameter
        hisat_args: supplementary arguments to pass to HISAT; these follow
            the -p parameter specified by num_threads and thus can override it
        samtools_exe: path to SAMTools executable

        Return value: None if successful or error message if unsuccessful
    """
    try:
        fastq_dump_command = (
                '{fastq_dump_exe} -I --split-files {sra_accession} -o {out}'
            ).format(
                fastq_dump_exe=fastq_dump_exe,
                sra_accession=sra_accession,
                out=temp_dir
            )
        exit_code = subprocess.Popen([fastq_dump_command], bufsize=-1).wait()
        if exit_code:
            return 'command "{}" exited with code {}.'.format(
                    fastq_dump_command, exit_code
                )
        fastq_files = os.listdir(temp_dir)
        if len(fastq_files) > 2:
            return (
                    'number of FASTQ files for SRA accession {} exceeds 2'
                ).format(sra_accession)
        hisat_command = (
                '{hisat_exe} -x {hisat_idx} -p {num_threads} '
                '{data} {hisat_args}'
            ).format(
                hisat_exe=hisat_exe, hisat_idx=hisat_idx,
                num_threads=num_threads, hisat_args=hisat_args,
                data=('-1 {} -2 {}'.format(*fastq_files)
                        if len(fastq_files) == 2
                        else '-U {}'.format(fastq_files[0]))
            )
        samtools_command = '{samtools_exe} view -bS >{bam_filename}'.format(
                samtools_exe=samtools_exe, bam_filename=bam_filename
            )
        align_command = ' | '.join([hisat_command, samtools_command])
        # Fail if any step in pipeline fails
        exit_code = subprocess.Popen(' '.join(
                        ['set -exo pipefail;', align_command]
                    ),
                bufsize=-1, stdout=sys.stdout, stderr=sys.stderr, shell=True,
                executable='/bin/bash').wait()
        if exit_code:
            return 'command "{}" exited with code {}.'.format(
                    align_command, exit_code
                )
        return None
    except Exception as e:
        # Miscellaneous exception
        from traceback import format_exc
        return 'error\n\n{}\ndownloading and aligning data.'.format(
                        format_exc()
                    )

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
    parser.add_argument('--hisat-idx', '-x', type=str, required=True,
                            help='path to HISAT index; enter its basename')
    parser.add_argument('--fastq-dump-exe', type=str, required=False,
                            default='fastq-dump',
                            help='path to fastq-dump executable')
    parser.add_argument('--samtools-exe', type=str, required=False,
                            default='samtools',
                            help='path to SAMTools executable')
    parser.add_argument('--out', type=str, required=False,
                            default='./',
                            help='output directory')
    parser.add_argument('--gtf', type=str, required=False,
                            default=None,
                            help=('gene annotation file; if provided, introns '
                                  'are harvested from it and passed to HISAT'))
    parser.add_argument('--num-processes', '-p', type=int, required=False,
                            default=4,
                            help=('number of simultaneous downloads/HISAT '
                                  'instances to run'))
    parser.add_argument('--num-threads', '-t', type=int, required=False,
                            default=4,
                            help=('number of cores allocated to each HISAT '
                                  'instance'))
    args = parser.parse_args()
    