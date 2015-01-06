#!/usr/bin/perl

use strict;
use Digest::MD5 qw(md5 md5_hex md5_base64);

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

my ($strSampleName, $strSampleGroup) = $strBAMfile ~= m/([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)\..+\.bam$/;

if($bVerbose)
{
	my $ts = localtime;
	print "[$ts] Processing the sample '$strSampleName' (group: '$strSampleGroup')\n";
}

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
	print "[$ts]\tFound $nChromosomes different chromosome names\n";
}

# Separate the alignments by chromosome name
my @arrFiles = ();
my @tmp = split(/\//, $strBAMfile);
my $strFilename = pop(@tmp);


foreach my $strChromosome (@arrChromosomes)
{
    my $strCMD = "samtools view -b $strBAMfile > $strOutputDir/${strChromosome}_$strFilename";
    print "$strCMD\n";
    `$strCMD`;
    push(@arrFiles, "$strOutputDir/${strChromosome}_$strFilename");
}

# We limit the number of worker threads to 16, therefore, simply take the first symbol of
# the hash.
my $strHash = md5("$strSampleName.$strSampleGroup");
my $strWorkerID = substr($strHash, 0, 1);

