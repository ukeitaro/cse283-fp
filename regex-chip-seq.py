import subprocess, re, os, argparse

curr_dir = os.getcwd()

def download_cell_type(cell_type, output_folder=curr_dir):

    # Query UCSC
    cmd = '''wget "http://genome.ucsc.edu/cgi-bin/hgFileSearch?hgsid=273586915&db=hg19&hgt_tsDelRow=&hgt_tsAddRow=&tsName=&tsDescr=&tsGroup=Any&fsFileType=Any&hgt_mdbVar1=dataType&hgt_mdbVal1=ChipSeq&hgt_mdbVar2=cell&hgt_mdbVal2={0}&hgt_mdbVar3=antibody&hgt_mdbVal3=Any&hgt_mdbVar4=view&hgt_mdbVal4=Peaks&hgfs_Search=search" -O {1}'''.format(cell_type, cell_type+'.html')

    subprocess.Popen(cmd, shell=True).wait()

    # Find URLs to all peak files
    x = open(cell_type + '.html').read()
    m = re.findall('window\.location.{100,200}gz', x)
    m = [a.split("window.location='")[1].split('.gz')[0] + '.gz' for a in m]
    for a in m[:5]: print a
    print len(m)

    # wget all peak files
    cmd_list = ['wget {0} -O {1} ; gunzip {1}'.format(x, os.path.join(output_folder, x.split('/')[-1])) for x in m]
    for cmd in zip(cmd_list):
        subprocess.Popen(cmd, shell=True).wait()

if __name__=='__main__':
    cell_types=['GM12878', 'h1-hESC', 'k562', 'hepg2', 'hela-s3', 'a549']
    for t in cell_types:
        if not os.path.isdir(t): os.mkdir(t)
        download_cell_type(t, output_folder=t)

