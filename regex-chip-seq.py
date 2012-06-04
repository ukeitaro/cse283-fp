import subprocess, re, os, argparse

curr_dir = os.getcwd()

def download_cell_type(cell_type, output_folder=curr_dir, download_peaks=True):

    cell_folder = os.path.join(output_folder, cell_type)
    if not os.path.isdir(cell_folder): os.makedirs(cell_folder)

    ##############################################################
    # Parse download URLs, antibodies, and cell types from query #
    ##############################################################

    html_string = open(os.path.join(output_folder, 'all_GM12878_K562_H1-HESC_HEP-G2_HELA-S3.html')).read()

    x = html_string.split("""</TBODY""")[0]
    x = x.split("""<TBODY class='sortable sorting'>""")[1]
    x = x.split("""<TR valign='top'><TD nowrap><input type='button' value='Download' onclick="window.location='""")
    x = x[1:] # Remove first element

    download_list = [a.split("';")[0] for a in x]
    antibody_list = [a.split("""<TD align='center' nowrap>""")[5].split()[0].split('</td>')[0] for a in x]
    cell_list = [a.split("""<TD align='center' nowrap>""")[3].split('</td>')[0] for a in x]
    
    # Remove extraneous modifiers and upper-case all antibody names
    antibody_list = [x.upper().split('_')[0] for x in antibody_list]  

    # d = [x.split('\t') for x in open('encode_antibodies.txt').read().split('\n') if x!='']
    # antibody_dict = dict([(x[1], ''.join(x[4].split('GeneCard:')[1].split())) for x in d if 'GeneCard' in x[4]])
    # antibody_dict = dict([(x[1], ''.join(x[4].split('GeneCard:')[1].split())) for x in d if 'GeneCard' in x[4]])

    # Dictionary: Entrez gene id to HUGO name
    entrez_id_2_hugo_names = dict([(x.split()[2], x.split()[1]) for x in open('List_of_TFs.txt').read().split('\n') if x!='' and x[0]!='#'])

    # Dictionary: antibody name to HUGO name (based on encode_antibodies.html)
    antibody_rows = [x for x in open('encode_antibodies.html').read().split('<TBODY>')[1].split('</TBODY>')[0].split('<TR>') if len(''.join(x.split()))!=0]
    antibody_names = [x.split('<TD')[3].split('>')[1].split('</TD')[0].split('_')[0].upper() for x in antibody_rows]  # Upper-case all antibody names
    antibody_names = [''.join(x.split('.')) for x in antibody_names]
    gene_names = [x.split('<TD>')[8].split('</TD>')[0] for x in antibody_rows]
    def convert_to_name(x):
        if 'www.genecards.org' in x:
            return x.split('gene=')[1].split('>')[0].split('"')[0].split("'")[0]
        elif 'ncbi.nlm.nih.gov' in x:
            entrez_gene_id = x.split('gene/')[1].split('>')[0].split('"')[0].split("'")[0]
            if entrez_id_2_hugo_names.has_key(entrez_gene_id):
                return entrez_id_2_hugo_names[entrez_gene_id]
            else:  return None
        else:      return None            
    antibody_dict = dict([(a, convert_to_name(g) if (g is not None) else a) for a, g in zip(antibody_names, gene_names)])

    #######################
    # wget all peak files #
    #######################

    # print cell_type, ',num antibodies:', len(set(antibody_list))
    # print cell_type, ',num convertible antibodies:', len(set([x for x in antibody_list if antibody_dict.has_key(x.upper())]))
    # print cell_type, ',inconvertible antibodies:', set([x for x in antibody_list if not antibody_dict.has_key(x)])

    # List of (peak file download URL, cell type, CHIP-Seq antibody)    
    # Filter for antibodies whose listed names are convertible to HUGO names
    ### triples = [[x,y,antibody_dict[z]] for x,y,z in zip(download_list, cell_list, antibody_list) if antibody_dict.has_key(z) and y==cell_type]
    triples = [[x,y,z] for x,y,z in zip(download_list, cell_list, antibody_list) if antibody_dict.has_key(z) and y==cell_type]
    download_list, cell_list, antibody_list = zip(*triples)

    # Make folders if they don't exist yet
    for a in antibody_list:
        if not os.path.isdir(os.path.join(cell_folder, a)): os.makedirs(os.path.join(cell_folder, a))

    # wget peak files (are these peaks over hg19 or hg18?)
    if download_peaks:
        cmd_list = ['wget {0} -O {1} ; gunzip -f {1}'.format(link, os.path.join(cell_folder, antibody, link.split('/')[-1])) for link, antibody in zip(download_list, antibody_list)]
        for cmd in cmd_list:
            print cmd
            subprocess.call(cmd, shell=True)

    peak_file_list = [os.path.join(cell_folder, antibody, link.split('/')[-1].split('.gz')[0]) for link, antibody in zip(download_list, antibody_list)]

    # Combine peaks for the same cell type and antibody.
    antibody_set = sorted(set(antibody_list))
    print 'Num antibodies:', len(antibody_set)
    for a in antibody_set:
        p = [peak_file for peak_file, antibody in zip(peak_file_list, antibody_list) if antibody==a]
        if len(p) > 0:
            cmd = "cat %s | cut -f1-3 > %s" % (' '.join(p), os.path.join(cell_folder, a, 'peaks.bed'))
            print cmd
            subprocess.call(cmd, shell=True)
    peak_file_list = [os.path.join(cell_folder, a, 'peaks.bed') for a in antibody_set]

    ###########################
    # BEDTools to Infer Edges #
    ###########################

    # 2.5 kb window around genes to account for peaks at proximal promoters
    window = '2500'

    edges, count = [], []

    for peak_file, antibody in zip(peak_file_list, antibody_set):
        output_prefix = '{0}_{1}'.format(cell_type, antibody)
        output_bed, output_names = [os.path.join(cell_folder, output_prefix+suffix) for suffix in ['.bed', '.txt']]

        # Use windowBed to get subset of TF BED intervals that are at most <window> positions away from some peak
        cmd = 'windowBed -u -w {0} -a {1} -b {2} | cut -f4 | sort -u'.format(window, 'List_of_TFs.bed', peak_file)
        print cmd
        bound_tfs = [x for x in subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].split('\n') if x!='']

        edges.extend([[antibody, x] for x in bound_tfs])
        count.append([antibody,str(len(bound_tfs))])

    open(os.path.join(cell_folder, 'count.txt'), 'w').write('\n'.join(['\t'.join(x) for x in count])+'\n')

    ####################
    # Infer edge signs #
    ####################
    # Infer signs (activating or repressing) based on POL2 co-localization with a TF

    # POL2 is also known as POLR2A
    pol2_bound_tfs = set([x[1] for x in edges if x[0]=='POL2' or x[0]=='POLR2A'])
    pol2_sign = dict([[x[1], ('+' if (x[1] in pol2_bound_tfs) else '-')] for x in edges])

    histones = '''
H2AZ
H3K27ac
H3K27me3
H3K36me3
H3K4me1
H3K4me2
H3K4me3
H3K79me2
H3K9ac
H3K9me1
H3K9me3'''.split()
    histones = [x.upper() for x in histones]

    # H3K4me3 is a mark for active transcription
    H3K4me3_bound_tfs = set([x[1] for x in edges if x[0]=='H3K4me3'.upper()])
    H3K4me3_sign = dict([[x[1], x[1] in H3K4me3_bound_tfs] for x in edges])

    # print H3K4me3_bound_tfs
    # print H3K4me3_sign.items()[:10]
    # 0 / asdf

    # H3K27me3 is a mark for repression
    H3K27me3_bound_tfs = set([x[1] for x in edges if x[0]=='H3K27me3'.upper()])
    H3K27me3_sign = dict([[x[1], x[1] in H3K27me3_bound_tfs] for x in edges])

    # Remove antibodies to histone marks in edges.txt
    # Convert antibody names to HUGO name
    edges = [[antibody_dict[x],y] for x,y in edges if x not in histones]
    edges = [[x,y] for x,y in edges if 'HIST' not in x]

    def get_sign(x):
        if (H3K27me3_sign[x] and H3K4me3_sign[x]) or ((not H3K27me3_sign[x]) and (not H3K4me3_sign[x])):
            return '?'
        elif (H3K27me3_sign[x] and (not H3K4me3_sign[x])):
            return '-'
        elif ((not H3K27me3_sign[x]) and H3K4me3_sign[x]):
            return '+'
        else:  assert False
    bound_tfs = set([x[1] for x in edges])
    sign_dict = dict([(x, get_sign(x)) for x in bound_tfs])

    signed_edges = [[a,b,sign_dict[b]] for a,b in edges]
    
    open(os.path.join(cell_folder, 'edges.txt'), 'w').write('\n'.join(['\t'.join(x) for x in edges])+'\n')
    open(os.path.join(cell_folder, 'edges_signed.txt'), 'w').write('\n'.join(['\t'.join(x) for x in signed_edges])+'\n')

if __name__=='__main__':

    # List of cell types
    
    cell_types=['HeLa-S3', 'HepG2', 'GM12878', 'H1-hESC', 'K562']
    #cell_types=['HeLa-S3', 'HepG2']

    origAssembly = 'Any' # 'hg18', 'hg19'
    # cmd = """wget 'http://genome.ucsc.edu/cgi-bin/hgFileSearch?hgsid=276423871&db=hg19&hgt_tsDelRow=&hgt_tsAddRow=&tsName=&tsDescr=&tsGroup=Any&fsFileType=Any&hgt_mdbVar1=cell&hgt_mdbVal1=GM12878&hgt_mdbVal1=H1-hESC&hgt_mdbVal1=K562&hgt_mdbVar2=view&hgt_mdbVal2=Peaks&hgt_mdbVar3=dataType&hgt_mdbVal3=ChipSeq&hgt_mdbVar4=origAssembly&hgt_mdbVal4=Any&hgfs_Search=search' -O all.html"""
    # print cmd
    # subprocess.call(cmd, shell=True)

    for t in cell_types:
        if not os.path.isdir(t): os.mkdir(t)
        download_cell_type(t, download_peaks=False)

