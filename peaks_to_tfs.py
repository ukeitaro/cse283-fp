import os, glob

if __name__=='__main__':

    # List of cell types
    cell_types=['GM12878', 'h1-hESC', 'k562', 'hepg2', 'hela-s3', 'a549']

    # List of TFs that were studied in ENCODE ChIP-Seq experiments
    tf_list = [x for x in open('tf_list.txt').read().split('\n') if x!='']

    # BED file of all TF genes in human genome (is this hg19?)
    all_tf = 'List_of_TFs.bed'

    # 2.5 kb window around genes to account for peaks at proximal promoters
    window = '25000'

    for t in cell_types:
        # Broad peaks
        all_peak_files = glob.glob(os.path.join(t, '*broadPeaks'))
        
        # Dictionary : TF --> list of peak files for ChIP-Seq on the TF
        tf_peak_files = [(x, [y for y in all_peak_files in x.upper() in y.upper()]) for x in tf_list]
        tf_peak_files = [a for a in tf_peak_files if len(a[1])>0]
        
        # Use BEDTools to match each TF's peaks with TF genes
        for tf, peak_files in tf_peak_files:
            for peak_file in peak_files:

                output_prefix = '{0}_{1}'.format(t, tf)

                # Use windowBed to get subset of TF BED intervals that
                # are at most <window> positions away from some peak
                cmd = 'windowBed -u -w {0} -a {1} -b {2} > {3}'.format(window, all_tf, peak_file, output_prefix+'.bed')
                subprocess.call(cmd, shell=True)        
                
                # Extract TF names from BED file
                column = None
                subprocess.call('cut -f{0} {1} > {2}'.format(column, output_prefix+'.bed', output_prefix+'.txt'))
                                
