import subprocess, re, os, argparse

curr_dir = os.getcwd()

def download_cell_type(cell_type, output_folder=curr_dir):

    # Query UCSC
    cmd = '''wget "http://genome.ucsc.edu/cgi-bin/hgFileSearch?hgsid=273586915&db=hg19&hgt_tsDelRow=&hgt_tsAddRow=&tsName=&tsDescr=&tsGroup=Any&fsFileType=Any&hgt_mdbVar1=dataType&hgt_mdbVal1=ChipSeq&hgt_mdbVar2=cell&hgt_mdbVal2={0}&hgt_mdbVar3=antibody&hgt_mdbVal3=Any&hgt_mdbVar4=view&hgt_mdbVal4=Peaks&hgfs_Search=search" -O {1}'''.format(cell_type, cell_type+'.html')

    subprocess.Popen(cmd, shell=True).wait()

    html_string = open(cell_type + '.html').read()



    ###################################################
    # Parse download URLs, antibodies, and cell types #
    ###################################################

    x = html_string
    x = x.split("""</TBODY""")[0]
    x = x.split("""<TBODY class='sortable sorting'>""")[1]
    x = x.split("""<TR valign='top'><TD nowrap><input type='button' value='Download' onclick="window.location='""")
    x = x[1:] # Remove first element

    download_list = [a.split("';")[0] for a in x]
    antibody_list = [a.split("""<TD align='center' nowrap>""")[4].split()[0].split('</td>')[0] for a in x]
    cell_list = [a.split('cell=')[1].split(';')[0] for a in x]

    d = [x.split('\t') for x in open('encode_antibodies.txt').read().split('\n') if x!='']
    d = dict([(x[1], x[4].split('GeneCard:')[1]) for x in d if 'GeneCard' in x[4]])
    antibody_dict = d
    
    # Read gene intervals 
    gene_loc = [x.split('\t')[1:] for x in open('List_of_TFs.txt').read().split('\n') if x!='']
    gene_loc = gene_loc[1:] # Read out header
    gene_set = set([x[1] for x in gene_loc])
    gene_loc_dict = dict()
    for gene_name, gene_id, gene_chr, gene_start, gene_end in gene_loc:

        gene_start, gene_end = int(gene_start), int(gene_end)
        gene_start = min(gene_start, gene_end)
        gene_end = max(gene_start, gene_end)

        if gene_loc_dict.has_key(gene_name):
            gene_loc_dict[gene_name][1] = min(gene_loc_dict[gene_name][1], gene_start)
            gene_loc_dict[gene_name][2] = max(gene_loc_dict[gene_name][2], gene_end)
        else:
            gene_loc_dict[gene_name] = [gene_chr, gene_start, gene_end]

        assert gene_loc_dict[gene_name][1] <= gene_loc_dict[gene_name][2]

    gene_loc_items = gene_loc_dict.items()
    gene_loc_items.sort(key = lambda a: a[1][1])


    # Write BED file of antibody intervals
    f = open('List_of_TFs.bed', 'w')
    f.write('\n'.join(['\t'.join(map(str,v)) + '\t' + k for k, v in gene_loc_items]))
    f.close()

    # wget all peak files
    triples = [[x,y,antibody_dict[z]] for x,y,z in zip(download_list, cell_list, antibody_list) if antibody_dict.has_key(z)]
    
    triples = triples[:1]

    for link, cell, antibody in triples:
        y = os.path.join(output_folder, cell, antibody)
        if not os.path.isdir(y): os.makedirs(y)
    cmd_list = ['wget {0} -O {1} ; gunzip {1}'.format(x, os.path.join(output_folder, cell, antibody, link.split('/')[-1])) for link, cell, antibody in triples]
    for cmd in cmd_list:
        #subprocess.Popen(cmd, shell=True).wait()
        pass

    # BED file of all TF genes in human genome (is this hg19?)
    all_tf = 'List_of_TFs.bed'

    ############
    # BEDTools #
    ############

    # 2.5 kb window around genes to account for peaks at proximal promoters
    window = '25000'

    for link, cell, antibody in triples:
        peak_file = os.path.join(output_folder, cell, antibody, link.split('/')[-1].split('.gz')[0])

        output_prefix = '{0}_{1}'.format(cell, antibody)

        # Use windowBed to get subset of TF BED intervals that
        # are at most <window> positions away from some peak
        cmd = 'windowBed -u -w {0} -a {1} -b {2} > {3}'.format(window, all_tf, peak_file, os.path.join(output_folder, cell, output_prefix+'.bed'))
        print cmd
        subprocess.call(cmd, shell=True)

        # Extract TF names from BED file
        column = 4
        cmd = 'cut -f{0} {1} > {2}'.format(column, os.path.join(output_folder, cell, output_prefix+'.bed'), os.path.join(output_folder, cell, output_prefix+'.txt'))
        subprocess.call(cmd, shell=True)
        print cmd
    
if __name__=='__main__':

    # List of cell types
    #cell_types=['GM12878', 'h1-hESC', 'k562', 'hepg2', 'hela-s3', 'a549']
    cell_types=['GM12878']

    for t in cell_types:
        if not os.path.isdir(t): os.mkdir(t)
        download_cell_type(t)

