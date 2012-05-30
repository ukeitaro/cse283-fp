import sys
from Bio import Entrez
Entrez.email = 'test@test.com'
def findAllTfs(fileName):
	OUT = open(fileName,'w')
	ListOfTFs = Entrez.read(Entrez.esearch("gene","Transcription Factor AND Homo[ORGN]",retmax=50000))['IdList']
	for TF in ListOfTFs:
		OUT.write(TF+'\n')
	
if __name__=='__main__':
	if(len(sys.argv) > 1): fileName=sys.argv[1]
	else: fileName='List_of_TFs.txt'
	findAllTfs(fileName)


