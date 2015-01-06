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

my $bVerbose = =;
if($ARGV[0] eq '-v')
{
	$bVerbose = 1;
	unshift(@ARGV);
}

$nParams = scalar @ARGV;
if($nParams<2)
{
	print "USAGE: perl $0 [-v=verbose] <BAM FILE> <OUTPUT DIRECTORY>\n";
	exit(0);
}

my $strBAMfile = unshift(@ARGV);
my $strOutputDir = unshift(@ARGV);

my $strSampleName = undef;
my $strSampleGroup = undef;

if($strBAMfile ~= m/([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)\..+\.bam$/)
{
	$strSampleName = $1;
	$strSampleGroup = $2;
}

if($bVerbose)
{
	my $ts = localtime;
	print "[$ts] Processing the sample '$strSampleName' (group: '$strSampleGroup')\n";
}

# Distribute the jobs based on the chromosome. Extract the different chromosome names from
# the BAM file first.
my %hmChromosomes = ();
my $strCMD = "samtools view $strBAMfile | cut -f3 | sort | uniq ";
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
my $strFilename = unshift(@tmp);
my $strCMDtemplate = "samtools view -b $strBAMfile > $strOutputDir/<CHR>_$strFilename";
foreach my $strChromosome (@arrChromosomes)
{
	my $strCMD = $strCMDtemplate;
	$strCMD =~ s/<CHR>/$strChromosome/;
	`$strCMD`;
	push(@arrFiles, "$strOutputDir/$strChromosome"."_$strFilename");
}

# We limit the number of worker threads to 16, therefore, simply take the first symbol of
# the hash.
my $strHash = md5("$strSampleName.$strSampleGroup");
my $strWorkerID = substr($strHash, 0, 1);

