
transcript_id_2_symbol = dict([x.split() for x in open('id_2_symbol.txt').read().split('\n') if x!='' and x[0]!='#'])

tf_gtf = [x.split('\t') for x in open('all_tf.gtf').read().split('\n') if x!='' and x[0]!='#']

transcript_id_list = [x[8].split(';')[0].split('"')[1] for x in tf_gtf]
symbol_list = [transcript_id_2_symbol[x] for x in transcript_id_list]

tf_gtf = [x[:8] + [x[8].replace(transcript_id, symbol, 1) + 'gene_name="%s"; ' % symbol] for x, transcript_id, symbol in zip(tf_gtf, transcript_id_list, symbol_list)]

open('all_tf_cufflinks.gtf', 'w').write('\n'.join(['\t'.join(x) for x in tf_gtf])+'\n')

