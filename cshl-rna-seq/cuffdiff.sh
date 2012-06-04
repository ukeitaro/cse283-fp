#!/bin/bash

H1_rep2=wgEncodeCshlLongRnaSeqH1hescNucleusPapAlnRep2.bam
GM12878_rep1=wgEncodeCshlLongRnaSeqGm12878NucleusPapAlnRep1.bam
K562_rep1=wgEncodeCshlLongRnaSeqK562NucleusPapAlnRep1.bam
GM12878_rep2=wgEncodeCshlLongRnaSeqGm12878NucleusPapAlnRep2.bam
K562_rep2=wgEncodeCshlLongRnaSeqK562NucleusPapAlnRep2.bam

CUFFLINKS_DIR="/home/mikeyu/cse283-fp/cufflinks-2.0.0.Linux_x86_64"

PROCESSES=15

$CUFFLINKS_DIR/cuffdiff -p $PROCESSES ../all_tf_cufflinks.gtf $K562_rep1,$K562_rep2 $GM12878_rep1,$GM12878_rep2 $H1_rep2