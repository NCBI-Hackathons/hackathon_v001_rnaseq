"""
align.py

NCBI Hackathon, RNA-seq team
January 5, 2015
Created by Abhi Nellore

Aligns RNA-seq FASTQs specified by a manifest file, each of whose lines has the
following format:

SRA accession number <TAB> sample group <TAB> sample name

Outputs BAM files. Each filename is in the following format:

<sample name>.<sample group>.<SRA accession>.bam

WARNING: fastq-dump creates cache directory in home directory, so use
vdb-config to change its location if home directory is on partition without
much space

Warnings: 1) index is not shared among hisat instances running in parallel;
--mm would permit this, but it appears to be buggy right now.
2) conversion to bam with samtools may fail because validation stringency
is strict; if that happens, use --gzip-output instead

Dependencies: HISAT, fastq-dump from sra-toolkit, samtools
"""
import multiprocessing
import subprocess
import tempfile
import atexit
import os
import shutil
import sys
import time
from collections import defaultdict
import signal

def init_worker():
    """ Prevents KeyboardInterrupt from reaching a pool's workers.

        Exiting gracefully after KeyboardInterrupt or SystemExit is a
        challenge. The solution implemented here is by John Reese and is from
        http://noswap.com/blog/python-multiprocessing-keyboardinterrupt .

        No return value.
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def download_and_align_data(sra_accession, out_filename, hisat_idx, temp_dir,
                            fastq_dump_exe='fastq-dump', hisat_exe='hisat',
                            hisat_args='', samtools_exe='samtools',
                            num_threads=4, intron_file=None,
                            gzip_output=False):
    """ Uses fastq-dump to download sample FASTQ(s) and aligns data with HISAT.

        sra_accession: sample accession number on SRA
        out_filename: full path to output filename
        hisat_idx: full path to HISAT index basename
        temp_dir: temporary directory for storing downloaded fastqs
        fastq_dump_exe: path to fastq-dump executable
        hisat_exe: path to HISAT executable
        hisat_args: supplementary arguments to pass to HISAT; these follow
            the -p parameter specified by num_threads and thus can override it
        samtools_exe: path to SAMTools executable
        num_threads: argument of HISAT's -p parameter
        intron_file: intron file to pass to HISAT or None if not present
        gzip_output: gzips sam output rather than converting to bam

        Return value: None if successful or error message if unsuccessful
    """
    try:
        fastq_dump_command = (
                '{fastq_dump_exe} -I --split-files {sra_accession} -O {out}'
            ).format(
                fastq_dump_exe=fastq_dump_exe,
                sra_accession=sra_accession,
                out=temp_dir
            )
        exit_code = subprocess.Popen(fastq_dump_command, bufsize=-1,
                                        shell=True).wait()
        if exit_code:
            return 'command "{}" exited with code {}.'.format(
                    fastq_dump_command, exit_code
                )
        fastq_files = [os.path.join(temp_dir, filename)
                        for filename in sorted(os.listdir(temp_dir))]
        if len(fastq_files) > 2:
            return (
                    'number of FASTQ files for SRA accession {} exceeds 2'
                ).format(sra_accession)
        hisat_command = (
                '{hisat_exe} -x {hisat_idx} -p {num_threads} '
                '{data} {intron_file} {hisat_args}'
            ).format(
                hisat_exe=hisat_exe, hisat_idx=hisat_idx,
                num_threads=num_threads, hisat_args=hisat_args,
                intron_file=('--known-splicesite-infile {}'.format(intron_file)
                                if intron_file is not None else ''),
                data=('-1 {} -2 {}'.format(*fastq_files)
                        if len(fastq_files) == 2
                        else '-U {}'.format(fastq_files[0]))
            )
        if gzip_output:
            pipe_command = 'gzip >{out_filename}'
        else:
            pipe_command = '{samtools_exe} view -bS - >{out_filename}'.format(
                    samtools_exe=samtools_exe, out_filename=out_filename
                )
        align_command = ' | '.join([hisat_command, pipe_command])
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
    start_time = time.time()
    import argparse
    # Print file's docstring if -h is invoked
    parser = argparse.ArgumentParser(description=__doc__, 
                formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--manifest', '-m', type=str, required=True,
                            help='path to manifest file')
    parser.add_argument('--hisat-exe', type=str, required=False,
                            default='hisat',
                            help='path to HISAT executable')
    parser.add_argument('--hisat-inspect-exe', type=str, required=False,
                            default='hisat-inspect',
                            help='path to HISAT inspect executable')
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
    parser.add_argument('--gzip-output', action='store_const', const=True,
                            default=False,
                            help=('gzips sam output of hisat; does not use '
                                  'samtools'))
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
    parser.add_argument('--temp', type=str, required=False,
                            default=None,
                            help=('where to store temporary files'))
    args = parser.parse_args()
    try:
        os.makedirs(args.out)
    except OSError:
        # Already exists?
        print >>sys.stderr, ('warning: could not create output directory; '
                             'it may already exist')
    if args.temp is not None:
        try:
            os.makedirs(args.temp)
        except OSError:
            # Already exists?
            print >>sys.stderr, ('warning: could not create temporary '
                                 'directory; it may already exist')
        else:
            atexit.register(shutil.rmtree, args.temp, ignore_errors=True)
    if args.gtf is not None:
        print 'harvesting introns from GTF file...'
        # Grab relevant refnames from hisat-inspect
        valid_chrs = set(
                subprocess.check_output(
                    '{hisat_inspect} -n {hisat_idx}'.format(
                    hisat_inspect=args.hisat_inspect_exe,
                    hisat_idx=args.hisat_idx
                ), shell=True).split('\n')
            )
        intron_dir = tempfile.mkdtemp(dir=args.temp)
        atexit.register(shutil.rmtree, intron_dir, ignore_errors=True)
        intron_file = os.path.join(intron_dir, 'introns.tab')
        with open(intron_file, 'w') as intron_stream:
            with open(args.gtf) as gtf_stream:
                exons = defaultdict(set)
                for line in gtf_stream:
                    if line[0] == '#': continue
                    tokens = line.strip().split('\t')
                    if (tokens[2].lower() != 'exon'
                        or tokens[0] not in valid_chrs): continue
                    sign = tokens[6]
                    assert sign in ['+', '-']
                    '''key: transcript_id
                       value: (rname, exon start (1-based), exon end (1-based))

                    transcript_id in token 12 is decked with " on the left and
                    "; on the right; kill them in key below.
                    '''
                    attribute = tokens[-1].split(';')
                    id_index = [i for i, name in enumerate(attribute)
                                if 'transcript_id' in name]
                    assert len(id_index) == 1, ('More than one transcript ID '
                                                'specified; '
                                                'offending line: {}').format(
                                                        line
                                                    ) 
                    id_index = id_index[0]
                    attribute[id_index] = attribute[id_index].strip()
                    quote_index = attribute[id_index].index('"')
                    exons[attribute[id_index][quote_index+1:-1]].add(
                            (tokens[0], int(tokens[3]), int(tokens[4]), sign)
                        )
                for transcript_id in exons:
                    exons_from_transcript = sorted(list(exons[transcript_id]),
                                                    key=lambda x: x[:3])
                    # Recall that GTF is end-inclusive
                    for i in xrange(1, len(exons_from_transcript)):
                        if (exons_from_transcript[i][0] 
                                == exons_from_transcript[i-1][0]):
                            # Kill any introns 4 bases or smaller
                            if (exons_from_transcript[i][1] 
                                - exons_from_transcript[i-1][2] < 5):
                                continue
                            print >>intron_stream, '\t'.join([
                                        exons_from_transcript[i][0],
                                        str(exons_from_transcript[i-1][2] + 1),
                                        str(exons_from_transcript[i][1] - 1),
                                        exons_from_transcript[i][3]
                                    ])
    pool = multiprocessing.Pool(args.num_processes, init_worker)
    try:
        with open(args.manifest) as manifest_stream:
            sample_count = 0
            return_values = []
            for i, line in enumerate(manifest_stream):
                if line[0] == '#': continue
                sra_accession, sample_group, sample_name = (
                        line.strip().split('\t')
                    )
                assert len(line.split('\t')) >= 3, (
                        'line "{}" does not have at least 3 fields.'
                    ).format(line.strip())
                if args.gzip_output:
                    out_filename = ''.join([sample_name,
                            sample_group, sra_accession, 'sam', 'gz'
                        ])
                else:
                    out_filename = '.'.join(
                            [sample_name, sample_group, sra_accession, 'bam']
                        )
                temp_dir = tempfile.mkdtemp(dir=args.temp)
                # Ensure that temporary directory is killed on SIGINT/SIGTERM
                atexit.register(shutil.rmtree, temp_dir, ignore_errors=True)
                pool.apply_async(download_and_align_data,
                                args=(sra_accession,
                                        os.path.join(args.out, out_filename),
                                        args.hisat_idx, temp_dir,
                                        args.fastq_dump_exe, args.hisat_exe,
                                        args.hisat_args, args.samtools_exe,
                                        args.num_threads, intron_file,
                                        args.gzip_output),
                                callback=return_values.append
                            )
                sample_count += 1
        pool.close()
        while len(return_values) < sample_count:
            errors = [return_value for return_value in return_values
                        if return_value is not None]
            if errors:
                raise RuntimeError('\n'.join(errors))
            sys.stdout.write(
                    'downloaded and aligned {}/{} datasets.\r'.format(
                            len(return_values), sample_count
                        )
                )
            time.sleep(0.2)
        print 'downloaded and aligned {} datasets in {} s.'.format(
                sample_count, time.time() - start_time
            )
    except (KeyboardInterrupt, SystemExit):
        pool.terminate()
        pool.join()