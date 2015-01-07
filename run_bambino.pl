#!/usr/bin/perl

use strict;
use File::Temp;


my $nParams = scalar @ARGV;
if($nParams<1)
{
	print "USAGE: perl $0 <BAM FILE>\n";
	exit(0);
}

my $strBAMfile = shift(@ARGV);

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

print "Sample\tGroup\tChromosome\tPosition\tRead\tReference\tCoverage\tPercentage\n";

open(BAMBINO_OUT, $strTempBambino);
my $strLine = <BAMBINO_OUT>;		# Skip the header
while($strLine = <BAMBINO_OUT>)
{
	chomp($strLine);
	my @arrChunks = split(/\t/, $strLine);
	next unless($arrChunks[5] eq 'SNP');
	next unless($arrChunks[28]);
	print "$strSampleName\t".
	      "$strSampleGroup\t".
	      "$arrChunks[3]\t".
	      "$arrChunks[4]\t".
	      "$arrChunks[10]\t".
	      "$arrChunks[9]\t".
	      "$arrChunks[7]\t".
	      "$arrChunks[8]\n";
}
close(BAMBINO_OUT);