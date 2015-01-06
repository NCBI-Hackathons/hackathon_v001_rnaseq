#!/usr/bin/perl

use strict;
use Digest::MD5 qw(md5 md5_hex md5_base64);
use File::Temp;

# File naming convention: sample-name.sample-group.original-name.bam
# Possible command-line parameters:
# perl distribute_bams.pl [-v=verbose] <BAM FILE> <OUTPUT DIRECTORY>

my $nParams = scalar @ARGV;
if($nParams<2)
{
	print "USAGE: perl $0 [-v=verbose] <BAM FILE> <OUTPUT DIRECTORY>\n";
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
	print "USAGE: perl $0 [-v=verbose] <BAM FILE> <OUTPUT DIRECTORY>\n";
	exit(0);
}

my $strBAMfile = shift(@ARGV);
my $strOutputDir = shift(@ARGV);

my $strSampleName = undef;
my $strSampleGroup = undef;
if($strBAMfile =~ m/([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)\..+\.bam$/)
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
my $hTempSAM = File::Temp->new(UNLINK => 1, SUFFIX => '.sam');
my $strTempSAM = $hTempSAM->filename;
my $strCMD = "samtools view -F 1540 -h $strTempSAM";
open(CMD_OUT, "$strCMD |");
while(my $strLine = <CMD_OUT>)
{
	chomp($strLine);
	if(substr($strLine, 0, 1) eq '@')
	{
		print $hTempSAM "$strLine\n";
		next;
	}
	if($strLine =~ m/NH:i:([0-9]+)/)
	{
		next unless($1==1);
	}
	else
	{
		print "ERROR: malformatted line: '$strLine'\n";
		exit(0);
	}
	print $hTempSAM "$strLine\n"; 
}
close(CMD_OUT);

# Sort and index the resulting filtered BAM file.
my $strBAMsorted = $strBAMfile;
$strBAMsorted =~ s/\.bam$/.sorted/;
$strCMD = "samtools view -S -b $strTempSAM | samtools sort - $strBAMsorted";

# Index the sorted BAM file.
if($bVerbose)
{
	my $ts = localtime;
	print "[$ts] Indexing the BAM file\n";
}
my $strCMD = "samtools index $strBAMsorted";
`$strCMD`;

# Distribute the jobs based on the chromosome. Extract the different chromosome names from
# the BAM file first.
my %hmChromosomes = ();
my $strCMD = "samtools view $strBAMfile | cut -f3 | sort -u";
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
my @arrFiles = ();
my @tmp = split(/\//, $strBAMfile);
my $strFilename = pop(@tmp);


foreach my $strChromosome (@arrChromosomes)
{
    my $strCMD = "samtools view -b $strBAMfile $strChromosome > $strOutputDir/${strChromosome}_$strFilename";
    `$strCMD`;
    push(@arrFiles, "$strOutputDir/${strChromosome}_$strFilename");
}

# We limit the number of worker threads to 16, therefore, simply take the first symbol of
# the hash.
my $strHash = md5("$strSampleName.$strSampleGroup");
my $strWorkerID = substr($strHash, 0, 1);

