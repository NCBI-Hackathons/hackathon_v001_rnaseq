#!/usr/bin/perl

use strict;
use File::Temp;

# File naming convention: chromosome_sample-name.sample-group.bam
# Possible command-line parameters:
# perl run_bambino.pl [-v=verbose] <BAM FILE> [OUTPUT FILE]

my $nParams = scalar @ARGV;
if($nParams<1)
{
	print "USAGE: perl $0 <BAM FILE> [OUTPUT FILE]\n";
	exit(0);
}

my $strBAMfile = shift(@ARGV);
my $strOutFile = shift(@ARGV);
if(!$strOutFile)
{
	$strOutFile = "$strBAMfile.bambino";
}

my $strSampleName = undef;
my $strSampleGroup = undef;
if($strBAMfile =~ m/([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)\.bam$/)
{
	$strSampleName = $1;
	$strSampleGroup = $2;
}

if(!$strSampleName || !$strSampleGroup)
{
	print "ERROR: the filename must follow the pattern: chromosome_sample-name.sample-group.bam\n";
	exit(0);
}

my $strBambinoRoot = "/blast/rna/Bambino";

my $hTempBambino = File::Temp->new(UNLINK => 1, SUFFIX => '.sam');
my $strTempBambino = $hTempBambino->filename;

my $strCMD = "java -Xmx3072m ".
                  "-cp $strBambinoRoot/bambino_bundle_1.06.jar Ace2.SAMStreamingSNPFinder ".
                  "-limit 100000 ".
                  "-bam $strBAMfile ".
                  "-tn T ".
                  "-fasta $strBambinoRoot/hg19.fasta ".
                  "-dbsnp-file $strBambinoRoot/hg19_snp135_binary.blob ".
                  "-of $strTempBambino 2>/dev/null";
                  
`$strCMD`;

open(OUT, ">$strOutFile");
open(BAMBINO_OUT, $strTempBambino);
my $strLine = <BAMBINO_OUT>;		# Skip the header
print OUT "Sample\tGroup\tChromosome\tPosition\tRead\tReference\tCoverage\tPercentage\n";
while($strLine = <BAMBINO_OUT>)
{
	chomp($strLine);
	my @arrChunks = split(/\t/, $strLine);
	next unless($arrChunks[5] eq 'SNP');
	next unless($arrChunks[28]);
	print OUT "$strSampleName\t".
	          "$strSampleGroup\t".
	          "$arrChunks[3]\t".
	          "$arrChunks[4]\t".
	          "$arrChunks[10]\t".
	          "$arrChunks[9]\t".
	          "$arrChunks[7]\t".
	          "$arrChunks[8]\n";
}
close(BAMBINO_OUT);
close(OUT);