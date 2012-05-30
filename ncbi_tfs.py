import sys
from Bio import Entrez
import MySQLdb as mdb


def findAllTfs(fileName):

	#get TFs from ncbi
	Entrez.email = 'test@test.com'
	ListOfTFs = Entrez.read(Entrez.esearch("gene","Transcription Factor AND Homo[ORGN]",retmax=50000))['IdList']
	

	#Get information from ucsc database 
	con = mdb.connect('genome-mysql.cse.ucsc.edu', 'genome', '', 'hg19')
	cur = con.cursor()	
	query = "SELECT kg.name, xref.geneSymbol, entrez.value, kg.chrom, kg.txStart, kg.txEnd FROM knownGene kg, knownToLocusLink entrez, kgXref xref WHERE entrez.name=kg.name AND xref.kgID=kg.name AND entrez.value IN ("+','.join(ListOfTFs)+")"	
	cur.execute(query)


	#Print to file	
	OUT = open(fileName,'w')
	OUT.write('Gene Id\tGene Symbol\tEntrez ID\tChromosome\tTranscription Start\tTranscription End\n')
	for i in range(cur.rowcount):
		data = cur.fetchone()	
		OUT.write(data[0]+'\t'+data[1]+'\t'+data[2]+'\t'+data[3]+'\t'+str(data[4])+'\t'+str(data[5])+'\n')
	OUT.close()

if __name__=='__main__':
	if(len(sys.argv) > 1): fileName=sys.argv[1]
	else: fileName='List_of_TFs.txt'
	findAllTfs(fileName)


