import subprocess, re, os, argparse

curr_dir = os.getcwd()

def download_cell_type(cell_type, output_folder=curr_dir):

    if not os.path.isdir(output_folder): os.mkdir(output_folder)

    ##############
    # Query UCSC #
    ##############
    
    html_file = os.path.join(output_folder, cell_type+'.html')
    cmd = '''wget "http://genome.ucsc.edu/cgi-bin/hgFileSearch?hgsid=273586915&db=hg19&hgt_tsDelRow=&hgt_tsAddRow=&tsName=&tsDescr=&tsGroup=Any&fsFileType=Any&hgt_mdbVar1=dataType&hgt_mdbVal1=ChipSeq&hgt_mdbVar2=cell&hgt_mdbVal2={0}&hgt_mdbVar3=antibody&hgt_mdbVal3=Any&hgt_mdbVar4=view&hgt_mdbVal4=Peaks&hgfs_Search=search" -O {1}'''.format(cell_type, html_file)
    subprocess.call(cmd, shell=True)
    html_string = open(html_file).read()


    ##############################################################
    # Parse download URLs, antibodies, and cell types from query #
    ##############################################################

    x = html_string
    x = x.split("""</TBODY""")[0]
    x = x.split("""<TBODY class='sortable sorting'>""")[1]
    x = x.split("""<TR valign='top'><TD nowrap><input type='button' value='Download' onclick="window.location='""")
    x = x[1:] # Remove first element

    download_list = [a.split("';")[0] for a in x]
    antibody_list = [a.split("""<TD align='center' nowrap>""")[4].split()[0].split('</td>')[0] for a in x]
    cell_list = [a.split('cell=')[1].split(';')[0] for a in x]

    d = [x.split('\t') for x in open('encode_antibodies.txt').read().split('\n') if x!='']
    antibody_dict = dict([(x[1], x[4].split('GeneCard:')[1]) for x in d if 'GeneCard' in x[4]])
    
    #########################
    # Read intervals of TFs #
    #########################
    
    # Rearrange columns into BED format and remove entries with weird
    # chromosome names, e.g. chr6_cox_...
    cmd = """awk '{ print $4"\t"$5"\t"$6"\t"$2}' {0}.txt | grep -v "chr*_" | tail -n +2 > {0}_normal_chr.txt""".format('List_of_TFs')
    subprocess.call(cmd, shell=True)

    # # Combine intervals with the same gene name
    # gene_loc = [x.split('\t')[1:] for x in open('List_of_TFs_normal_chr.txt').read().split('\n') if x!='']
    # gene_loc = gene_loc[1:]  # Read out header
    # gene_set = set([x[1] for x in gene_loc])  # Unique set of gene names
    # gene_loc_dict = dict()  # Dictionary: gene name -->  [chromosome, start, end]
    # for gene_name, gene_id, gene_chr, gene_start, gene_end in gene_loc:

    #     gene_start, gene_end = int(gene_start), int(gene_end)
    #     gene_start = min(gene_start, gene_end)
    #     gene_end = max(gene_start, gene_end)

    #     if gene_loc_dict.has_key(gene_name):
    #         x = gene_loc_dict[gene_name]
    #         x[1:3] = [min(x[1], gene_start), max(x[2], gene_end)]
    #         assert x[0]==gene_chr
    #     else:
    #         gene_loc_dict[gene_name] = [gene_chr, gene_start, gene_end]  
      
    #     assert gene_loc_dict[gene_name][1] <= gene_loc_dict[gene_name][2]

    #######################
    # wget all peak files #
    #######################

    # List of (peak file download URL, cell type, CHIP-Seq antibody)
    triples = [[x,y,antibody_dict[z]] for x,y,z in zip(download_list, cell_list, antibody_list) if antibody_dict.has_key(z)]

    triples = triples[:1]

    # Make folders if they don't exist yet
    for link, cell, antibody in triples:
        y = os.path.join(output_folder, cell, antibody)
        if not os.path.isdir(y): os.makedirs(y)

    # wget peak files (are these peaks over hg19 or hg18?)
    cmd_list = ['wget {0} -O {1} ; gunzip {1}'.format(link, os.path.join(output_folder, cell, antibody, link.split('/')[-1])) for link, cell, antibody in triples]
    for cmd in cmd_list:
        print cmd
        subprocess.Popen(cmd, shell=True).wait()
        pass
    
    # List of (peak file, cell type, CHIP-Seq antibody)
    triples = [[os.path.join(output_folder, cell, antibody, link.split('/')[-1].split('.gz')[0]), cell, antibody] for link, cell, antibody in triples]

    # Combine peaks for the same cell type and antibody.  Merge peaks into non-overlapping peaks
    cell_types = set([x[1] for x in triples])
    antibodies = set([x[2] for x in triples])
    for c in cell_types:
        for a in antibodies:
            peak_file_list = [peak_file for peak_file, cell, antibody in triples if cell==c and antibody==a]
            if len(peak_file_list) > 0:
                # Merge
                cmd = "cat %s > %s" % (' '.join(peak_file_list), os.path.join(output_folder, c, a, 'peaks.bed'))
                print cmd
                subprocess.call(cmd, shell=True)

    0 / asdf

    #########################
    # Read intervals of TFs #
    #########################                                                                                                                                                                                      

    # Rearrange columns into BED format and remove entries with weird
    # chromosome names, e.g. chr6_cox_...
    cmd = """awk '{ print $4"\t"$5"\t"$6"\t"$2}' %s.txt | grep -v 'chr*_' | tail -n +2 > %s.bed""" % ('List_of_TFs', 'List_of_TFs')
    subprocess.call(cmd, shell=True)
    
    # # Read gene intervals 
    # # Combine intervals with the same gene name
    # gene_loc = [x.split('\t') for x in open('List_of_TFs_normal_chr.txt').read().split('\n') if x!='']
    # for a in gene_loc[:5]: print a
    # gene_set = set([x[1] for x in gene_loc])
    # gene_loc_dict = dict()
    # for gene_chr, gene_start, gene_end, gene_name in gene_loc:

    #     gene_start, gene_end = int(gene_start), int(gene_end)
    #     gene_start = min(gene_start, gene_end)
    #     gene_end = max(gene_start, gene_end)

    #     if gene_loc_dict.has_key(gene_name):
    #         x = gene_loc_dict[gene_name]
    #         x[1:3] = [min(x[1], gene_start), max(x[2], gene_end)]
    #         if x[0]!=gene_chr:
    #             print x, gene_name, gene_chr
    #         assert x[0]==gene_chr
    #     else:
    #         gene_loc_dict[gene_name] = [gene_chr, gene_start, gene_end]  
      
    #     assert gene_loc_dict[gene_name][1] <= gene_loc_dict[gene_name][2]

    # gene_loc_items = gene_loc_dict.items()
    # gene_loc_items.sort(key = lambda a: a[1][1])

    # # Write BED file of antibody intervals
    # f = open('List_of_TFs.bed', 'w')
    # f.write('\n'.join(['\t'.join(map(str,v)) + '\t' + k for k, v in gene_loc_items]))
    # f.close()

    # BED file of all TF genes in human genome (is this hg19?)
    all_tf = 'List_of_TFs.bed'

    ############
    # BEDTools #
    ############

    # 2.5 kb window around genes to account for peaks at proximal promoters
    window = '25000'

    for peak_file, cell, antibody in triples:
        #peak_file = os.path.join(output_folder, cell, antibody, link.split('/')[-1].split('.gz')[0])

        output_prefix = '{0}_{1}'.format(cell, antibody)
        output_bed = os.path.join(output_folder, cell, output_prefix+'.bed')
        output_names = os.path.join(output_folder, cell, output_prefix+'.txt')

        # Use windowBed to get subset of TF BED intervals that
        # are at most <window> positions away from some peak
        cmd = 'windowBed -u -w {0} -a {1} -b {2} > {3} ; cut -f{4} {3} {5}'.format(window, all_tf, peak_file, output_bed, column, output_names)
        print cmd
        subprocess.call(cmd, shell=True)
    
if __name__=='__main__':

    # List of cell types
    #cell_types=['GM12878', 'h1-hESC', 'k562', 'hepg2', 'hela-s3', 'a549']
    cell_types=['GM12878']

    for t in cell_types:
        if not os.path.isdir(t): os.mkdir(t)
        download_cell_type(t)

