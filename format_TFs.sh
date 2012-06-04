#!/bin/bash

########################
# Format List_of_TFs.txt


# BED file of TF genomic intervals.  Removed TFs in weird chromosomes likes 'chr6_cox...'
awk '{ print $4"\t"$5"\t"$6"\t"$2}' List_of_TFs.txt | grep -v 'chr.*_' | tail -n +2 | sort -k1,1 -k2,2 > List_of_TFs.bed

# List of all TF names
cut -f4 List_of_TFs.bed | sort -u > all_tf.txt