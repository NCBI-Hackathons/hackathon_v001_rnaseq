#!/usr/bin/perl

use strict;
use File::Temp;

# File naming convention: sample-name.sample-group.original-name.sam.gz
# Possible command-line parameters:
# perl distribute_bams.pl [-v=verbose] <SAM.GZ FILE> <OUTPUT DIRECTORY>

my $TEMPDIR = '/blast/rna/BAM/tmp';

my $nParams = scalar @ARGV;
if($nParams<2)
{
	print "USAGE: perl $0 [-v=verbose] <SAM.GZ FILE> <OUTPUT DIRECTORY>\n";
	exit(0);
}

my $bVerbose = 0;
if($ARGV[0] eq '-v')
{
	$bVerbose = 1;
	shift(@ARGV);
}

$nParams = scalar @ARGV;
if($nParams<2)
{
	print "USAGE: perl $0 [-v=verbose] <SAM.GZ FILE> <OUTPUT DIRECTORY>\n";
	exit(0);
}

my $strBAMfile = shift(@ARGV);
my $strOutputDir = shift(@ARGV);

my $strSampleName = undef;
my $strSampleGroup = undef;
if($strBAMfile =~ m/([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)\..+\.sam.gz$/)
{
	$strSampleName = $1;
	$strSampleGroup = $2;
}

if(!$strSampleName || !$strSampleGroup)
{
	print "ERROR: the filename must follow the pattern: sample-name.sample-group.original-name.bam\n";
	exit(0);
}

if($bVerbose)
{
	my $ts = localtime;
	print "[$ts] Processing the sample '$strSampleName' (group: '$strSampleGroup')\n";
}

# First, remove the PCR duplicates, low quality, unmapped and non-unique reads.
if($bVerbose)
{
	my $ts = localtime;
	print "[$ts] Removing the PCR duplicates, low quality, unmapped and non-unique reads\n";
}
my $hTempSAM = File::Temp->new(UNLINK => 1, SUFFIX => '.sam', DIR => $TEMPDIR);
my $strTempSAM = $hTempSAM->filename;
my $strCMD = "zcat $strBAMfile | python filter.py | samtools view -S -F 1540 -h - 2>/dev/null";
my $nReads = 0;
open(CMD_OUT, "$strCMD |");
while(my $strLine = <CMD_OUT>)
{
	chomp($strLine);
	if(substr($strLine, 0, 1) eq '@')
	{
		print $hTempSAM "$strLine\n";
		next;
	}
	$nReads++;
	print $hTempSAM "$strLine\n"; 
}
close(CMD_OUT);
if($bVerbose)
{
	my $ts = localtime;
	print "\t[$ts] Processed $nReads reads\n";
}

# Sort and index the resulting filtered BAM file.
if($bVerbose)
{
	my $ts = localtime;
	print "[$ts] Sorting and indexing the BAM file\n";
}
my $strBAMsorted = $strBAMfile;
$strBAMsorted =~ s/\.sam.gz$/.sorted/;
$strCMD = "samtools view -S -b $strTempSAM > $strBAMsorted 2>/dev/null";
`$strCMD`;
$strCMD ="samtools sort $strBAMsorted $strBAMsorted 2>/dev/null";
`$strCMD`;
$strCMD = "rm $strBAMsorted";
`$strCMD`;
$strCMD = "samtools index $strBAMsorted.bam 2>/dev/null";
`$strCMD`;

# Split the jobs based on the chromosome. Extract the different chromosome names from
# the BAM file first.
my %hmChromosomes = ();
$strCMD = "samtools view $strBAMsorted.bam 2>/dev/null | cut -f3 | sort -u";
open(CMD_IN, "$strCMD |");
while(my $strLine = <CMD_IN>)
{
	chomp($strLine);
	$hmChromosomes{$strLine} = 1;
}
close(CMD_IN);

my @arrChromosomes = keys %hmChromosomes;

if($bVerbose)
{
	my $ts = localtime;
	my $nChromosomes = scalar @arrChromosomes;
	print "[$ts] Found $nChromosomes different chromosome names\n";
}

# Separate the alignments by chromosome name
my @tmp = split(/\//, $strBAMfile);
my $strFilename = pop(@tmp);

foreach my $strChromosome (@arrChromosomes)
{
    my $strCMD = "samtools view -b -h $strBAMsorted.bam $strChromosome > $strOutputDir/${strChromosome}_$strSampleName.$strSampleGroup.bam";
    `$strCMD`;
}