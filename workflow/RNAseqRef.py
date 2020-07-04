#!/usr/bin/python 
# -*- coding: utf-8 -*-
# by Yan Pengcheng yanpc@bcc.ac.cn
# Comprehansive RNA-seq analysis pipeline on BBC cluster
# Version 2.1    2016-02-27
# use graph structure to orgnise pipeline
# replace optparse module with argparse
# plan to abandon XML format config file

'''

Tophat WRAPER on BCC cluster

Batch mode transcriptome for BCC platform

'''

import os, sys
import time
from argparse import ArgumentParser
import networkx as nx

lib_path = os.path.abspath('/share/home/yanpc/pipelines/RNAseqRef_test')
sys.path.append(lib_path+'/lib')

from Shell import *
from Task import *
from ParseLibrary import parse_cfg,check_cfg


def get_parameters():

    par = {}
    par['MAX_THREADS'] = 12
    lib_path = os.path.dirname(sys.argv[0])
    par['BIN'] = os.path.abspath(lib_path+'/script')
    par['CWD'] = os.getcwd()

    argP = ArgumentParser()
    argP.add_argument('-c','--config', dest='config', help='Library config file in XML', required=True)
#    argP.add_argument('-f','--reference', dest='reference', help='Reference genome sequence in FASTA', required=True)
#    argP.add_argument('-g','--gtf', dest='gtf', help='Reference gene feature in GTF', required=True)
#    argP.add_argument('-m','--go', dest='biomart', help='Reference gene GO annotation from bioMart', required=True)
#    argP.add_argument('-s','--species', dest='species', help='Species code like KEGG', required=True)
#    argP.add_argument('-d','--min-depth', dest='d', type=int, default=3, help='Min depth for SNP calling')
#    argP.add_argument('-D','--max-depth', dest='D', type=int, default=2000, help='Max depth for SNP calling')
    argP.add_argument('-l','--log', dest='log', default='run.log', help='Log file')
    args = argP.parse_args()
    par.update(args.__dict__)

    par['config'] =os.path.abspath(par['config'])

    par['library'] = parse_cfg(par['config'])

    prefix = par['library']['genome']
    par['genome'] = '/share/home/bioinfor/database/ref/transcriptome/' + prefix + '/' + prefix + '.fa'
    par['gtf'] = '/share/home/bioinfor/database/ref/transcriptome/' + prefix + '/' + prefix + '.gtf'
    par['ko'] = '/share/home/bioinfor/database/ref/transcriptome/' + prefix + '/kegg/' + prefix + '.list'
    par['biomart'] = '/share/home/bioinfor/database/ref/transcriptome/' + prefix + '/kegg/biomart.txt'
    par['d'] = par['library']['par']['d']
    par['D'] = par['library']['par']['D']
    par['species'] = prefix

    if not os.access(par['genome'], os.R_OK) :
        sys.stderr.write('reference genome file is not accessable\n')
        sys.exit(1)

	if not os.access(par['gtf'], os.R_OK) :
		sys.stderr.write('reference gtf file is not accessable\n')
		sys.exit(1)

    if not os.access(par['biomart'], os.R_OK) :
        sys.stderr.write('biomart file is not accessable\n')
        sys.exit(1)


    if not check_cfg(par['library']) : sys.exit(1)

    return par
	

############################### TRANSCRIPTOME #######################################

pars = get_parameters()
species  = pars['species']
config = pars['config']
logFile = pars['log']
cwd = pars['CWD']
genome = pars['genome']
gtf = pars['gtf']
ko = pars['ko']
biomart = pars['biomart']
MAX_THREADS = pars['MAX_THREADS']
Bin = pars['BIN']+'/'
d = pars['d']
D = pars['D']

#	"PWD" =>	#task working dir, will be created automatically
#	"DESC" =>	#task description, will be printed in log
#	"CMD" =>	#task command, must contain input, output and parameters
#	"INPUT" =>	#input file array
#	"OUTPUT" =>	#output file array
#	"TYPE" =>	#job type: (JMS|SYS):(\d+):(\d+), 
			# JMS for LSF, PBS or SGE; SYS for shell; node number and core number
#	"NAME" =>	#job name

# start run pipeline
############################### TRANSCRIPTOME #######################################
logging.basicConfig(level=logging.INFO,
		    format='%(asctime)-4s %(name)s:%(levelname)-8s %(message)s',
		    datefmt='%Y-%m-%d %H:%M',
		    filename=logFile)
logger = logging.getLogger('FLOW')
logger.info("start workflow")
logger.info('initial all jobs in workflow')

os.environ['PATH'] += ':'+Bin
os.putenv('PYTHONPATH', Bin+'/lib')

jobArray = []

BAMfs = cwd+'/mapping/{}/accepted_hits.bam'
ASGTFfs = cwd+'/AS/{}.gtf'
sampleList = []
for l in pars['library']['lib'] :
    sample = l['name']
    sampleList.append(sample)
    #insert_size = l['insert_size']
    left = cwd+'/clean_data/'+sample+'_R1.fq'
    right = cwd+'/clean_data/'+sample+'_R2.fq'

    jobArray.append(({'PWD' :'clean_data', 'DESC':'Processing sample ['+sample+']', 'INPUT':{'I1':l['left'], 'I2':l['right']},
		    'OUTPUT':{'O1':cwd+'/clean_data/'+sample+'_stats.txt','O2':left},
		    'CMD':Bin+'refRNA_readTrim -t AVG -q 30 -l ${I1} -r ${I2} -s '+sample, 'NAME':'preprocess', 'TYPE':'SYS:1:12'}))

    jobArray.append(({'PWD' :'mapping',
		    'DESC'  :'Using Tophat to alian reads search against '+genome,
		    'INPUT' :{'I1':left,'I2':right},
		    'OUTPUT':{'O1':BAMfs.format(sample)},
		    'CMD'   :'wrapperHISAT -p '+str(MAX_THREADS)+' -o {0} '.format(sample)+'-x '+genome[:-3]+' -l ${I1} -r ${I2}', 
		    'NAME'  :'mapping', 'TYPE'  :'SYS:1:'+str(MAX_THREADS)}))
 
    jobArray.append(({'PWD' :'mapping',
		    'DESC'  :'Stistic mapping results for '+sample,
		    'INPUT' :{'I1':BAMfs.format(sample)},
		    'OUTPUT':{'O1':'/'.join([cwd,'mapping',sample+'-mapping.xls'])},
		    'CMD'   :'bam_stat.py -i ${I1} > ${O1}',
		    'NAME'  :'stat_map',
		    'TYPE'  :'SYS:1:1'}))

    #jobArray.append(Task({'PWD' :'mapping',
#			'DESC'  :'Stistic mapping depth for '+sample,
#			'INPUT' :{'I1':cwd+'/mapping/'+sample+'/accepted_hits.bam','I2':genome},
#			'OUTPUT':{'O1':cwd+'/mapping/'+sample+'-depth.wig'},#,"$sample\_depth.png")
#			'CMD'   :Bin+'/IGVTools/igvtools count ${I1} ${O1} ${I2}; perl '+Bin+'/plotDepth_igvtools.pl -d ${O1} ',
#			'NAME'  :'depth',
#			'TYPE'  :'JMS:1:1'}))

    jobArray.append(({'PWD' :'expression',
		    'DESC'  :'Estimate expression level for '+sample,
		    'INPUT' :{'I1':gtf,'I2':BAMfs.format(sample)},
		    'OUTPUT':{'O1':cwd+'/expression/'+sample+'.fpkm.xls'},
		    'CMD'   :'stringtie -p '+str(MAX_THREADS)+' -G ${I1} -o '+sample+'.gtf -e -A '+sample+'.fpkm.xls ${I2}',
		    'NAME'  :'expression',
		    'TYPE'  :'SYS:1:12'}))

    jobArray.append(({'PWD' :'AS',
		    'DESC'  :'Assemble noval transcripts for '+sample,
		    'INPUT' :{'I1':BAMfs.format(sample)},
		    'OUTPUT':{'O1':ASGTFfs.format(sample)},
		    'CMD'   :'stringtie -p '+str(MAX_THREADS)+' -o '+sample+'.gtf ${I1}',
		    'NAME'  :'assemble',
		    'TYPE'  :'SYS:1:12'}))

    jobArray.append(({'PWD' :'SNP-calling',
		    'DESC'  :'detect cSNP for all samples',
		    'INPUT' :{'I1':genome,'I2':BAMfs.format(sample)},
		    'OUTPUT':{'O1':'/'.join([cwd,'SNP-calling',sample+'.bcf']),'O2':'/'.join([cwd,'SNP-calling',sample+'.vcf'])},
		    #'CMD'   :'samtools mpileup -q 20 -Q 20 -m 5 -uf ${I1} ${I2} > ${O1}',
		    'CMD'   :'samtools mpileup -C50 -q 20 -uf ${I1} ${I2} | bcftools call -vmO z -o ${O1}; bcftools filter -O v -o ${O2} -s LOWQUAL -i \'%QUAL>10 && (DP4[2]+DP4[3]) >2\' ${O1}',#.gz; bgzip -d ${O1}.gz

		    'NAME'  :'SNPCalling',
		    'TYPE'  :'SYS:1:1'}))

#    sys.stderr.write('Sample ['+sample+'] was successfully processed!\n')

sampleNum = len(sampleList)
inputList = [ASGTFfs.format(s) for s in sampleList]
tmpKeys = ['I%d'%i for i in range(2,sampleNum+2)]
gtfL = dict( (keys,values) for keys,values in zip(tmpKeys,inputList))
gtfL['I1'] = gtf

fw = open(cwd+'/inputList','w')
map(fw.write, ['%s\n'%s for s in inputList])
fw.close()

jobArray.append(({'PWD' :'AS',
		'DESC'  :'Assemble transcripts all samples and merge all samples result to detect AS events',
		'INPUT' :gtfL,
		'OUTPUT':{'O1':cwd+'/AS/merged.gtf'},
		'CMD'   :'stringtie --merge -p '+str(MAX_THREADS)+' -G ${I1} -o merged.gtf '+cwd+'/inputList',
		'NAME'  :'mergeTrans',
		'TYPE'  :'SYS:1:12'}))

groupInput = ','.join([l['group'] for l in pars['library']['lib']])
tmpKeys = ['I%d'%i for i in range(1,sampleNum+1)]

level = 'genes' # or isoforms
FPKMfs = cwd+'/expression/{}.fpkm.xls'
FPKMList = [FPKMfs.format(s) for s in sampleList]
BAMList = [BAMfs.format(s) for s in sampleList]

jobArray.append(({'PWD' :'expression',
		'DESC'  :'extract expression value and plot',
		'INPUT' :dict( (keys,values) for keys,values in zip(tmpKeys,FPKMList)),
		'OUTPUT':{'O1':cwd+'/expression/expression_table.xls'},
		'CMD'   :Bin+'refRNA_extractANDplotExpr '+gtf+' '+groupInput+' '+' '.join(FPKMList),
		'NAME'  :'plot',
		'TYPE'  :'SYS:1'}))

jobArray.append(({'PWD' :'expression',
		'DESC'  :'get read count for genens',
		'INPUT' :dict( (keys,values) for keys,values in zip(tmpKeys,BAMList)),
		'OUTPUT':{'O1':cwd+'/expression/count_table.xls'},
		'CMD'   :Bin+'refRNA_readCount '+gtf+' '+' '.join(BAMList),
		'NAME'  :'count',
		'TYPE'  :'SYS:1'}))

jobArray.append(({'PWD'  :'AS',
		'DESC'  :'Compare merged transcripts to reference transcripts and detect new transcripts',
		'INPUT' :{'I1':genome,'I2':gtf,'I3':cwd+'/AS/merged.gtf'},
		'OUTPUT':{'O1':cwd+'/AS/new_transcripts.gtf'},
		'CMD'   :Bin+'refRNA_newTrans -g ${I1} -r ${I2} -n ${I3} -s '+species+' -o ${O1}',
		'NAME'  :'newTrans',
		'TYPE'  :'SYS:1'}))

cluster = []
for p in pars['library']['compare'] :
    a = p['groupA']
    b = p['groupB']
    group_a_input = ''
    group_b_input = ''
    for l in pars['library']['lib'] :
        if l['group'] == a : group_a_input += ' '+l['name']
        if l['group'] == b : group_b_input += ' '+l['name']

    compare_output = a+'-VS-'+b
    cluster.append(compare_output)

jobArray.append(({'PWD' :'differential',
        'DESC'  :'Compare between groups: '+a+' and '+b,
	    'INPUT' :{'I1':cwd+'/expression/count_table.xls','I2':biomart},
	    'OUTPUT':{'O1':'/'.join([cwd,'differential',compare_output,compare_output+'.diff.xls'])},
	    #'OUTPUT':{'O1':'/'.join([cwd,'differential',compare_output,compare_output+'.xls'])},
	    #'CMD'   :'refRNA_DGE -d ${I1} -g1 '+group_a_input+' -g2 '+group_b_input+' -p 0.05 -f 0.1 -o '+compare_output+';refRNA_topGO -g ${I2} -d ${O1} -f '+compare_output+' -a 2 -o ../GO/; refRNA_KEGG --outdir ../pathway/'+compare_output+' --dge ${O1} --sp '+species+' --cvt ${I2}',
	    'CMD'   :Bin+'refRNA_DGE -d ${I1} -g1 '+group_a_input+' -g2 '+group_b_input+' -p 0.05 -f 0.1 -o '+compare_output+';refRNA_topGO -g ${I2} -d ${O1} -f '+compare_output+' -a 2 -o '+compare_output+';refRNA_KEGG --outdir ../pathway/'+compare_output+' --dge ${O1} --ko '+ko+' --cvt ${I2}',
	    'NAME'  :'DE',
	    'TYPE'  :'SYS:1:1'}))

jobArray.append(({'PWD' :'cluster',
		'DESC'  :'Cluster DE genes from: '+''.join(cluster),
		'INPUT' :{'I1':cwd+'/expression/expression_table.xls'},
		'OUTPUT':{'O1':cwd+'/cluster/cluster_heatmap.png'},
		'CMD'   :Bin+'refRNA_getDEExprANDplot -f '+cwd+'/differential/*/*.diff.xls -d ${I1} -o cluster_in.xls;',
		'NAME'  :'cluster',
		'TYPE'  :'SYS:1:1'}))

# load template to generate report
jobArray.append(({'DESC'  :'Make HTML report',
		'INPUT' :{'I1':config,'I2':genome,'I3':gtf,'I4':biomart},
		'OUTPUT':{'O1':cwd+'/report/index.html'},
		'CMD'   :Bin+'refRNA_report -c ${I1} -f ${I2} -g ${I3} -m ${I4} -s '+species+' -o report;',
		'NAME'  :'report',
		'TYPE'  :'SYS:1:1'}))

logger.info('Set up '+str(len(jobArray))+' jobs in workflow')

for j in range(len(jobArray)):
    job = Task(jobArray[j])
    #if job._status == 'running':
	#nstatus = job.task_status()
    #if job._status == 'done' or job._status == 'skip':
#	continue
    #if job._status == 'error':
    #    job.task_clean()

    time.sleep(10)

logger.info("start clean tmpfiles")
os.system('rm -f '+cwd+'/AS/inputList')
os.system('rm -f '+cwd+'/mapping/*.bed')
os.system('zip -r report.zip '+cwd+'/report/*')
logger.info("workflow finished\n\n")

sys.exit(0)
