#!/bin/bash
usage(){
	echo "Usage: $0 directory"
	exit 1
}
 
# define is_directory_exits function
# $f -> store argument passed to the script
if_directory_exists(){
	local d="$1"
	[[ -d "$d" ]] && return 0 || return 1
}
# invoke  usage
# call usage() function if filename not supplied
[[ $# -eq 0 ]] && usage
 
# Invoke is_directory_exists
if ( if_directory_exists "$1" )
then
 echo "Directory Found"
else
 echo "Creating directory $1"
 mkdir $1
fi

#Download files
wget ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeSydhTfbs/*.narrowPeak.gz -P "$1"
wget ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeUchicagoTfbs/*.narrowPeak.gz -P "$1"
wget ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeUwTfbs/*.narrowPeak.gz -P "$1"
 
