# library for transys 
# -*- coding: utf-8 -*-
# by Yan Pengcheng yanpc@bcc.ac.cn
# Comprehansive RNA-seq analysis pipeline on BBC cluster
# Version 2.1    2016-02-27
# use graph structure to orgnise pipeline
# replace optparse module with argparse
# plan to abandon XML format config file
# reformat the config file:
# [sample]
# #group	sample	file1	file2
# [compare]
# #groupA	groupB

'''

Tophat WRAPER on BCC cluster

Batch mode transcriptome for BCC platform

'''

import os, sys

def parse_cfg(cfg):

    data = {'lib':[],'group':[],'compare':[], 'par':{}}
    section = ''
    cf = open(cfg,'r')
    for l in cf :
	tab = l.strip().split('\t')
# skip blank line in config file
        if tab[0] == '' : continue
        if tab[0] == '[sample]' :
            section = tab[0]
            continue
        if tab[0] == '[compare]' :
            section = tab[0]
            continue
        if tab[0] == '[genome]' :
            section = tab[0]
            continue
        if tab[0] == '[par]' :
            section = tab[0]
            continue
# start parse sample sheet
        if section == '[sample]' :
# skip header line in config file
	    if "#" in tab[0] : continue
	    if len(tab) == 3:
	        data['lib'].append({'name':tab[1],'group':tab[0],'type':'SE','left':os.path.abspath(tab[2])})
	    elif len(tab) == 4:
	        data['lib'].append({'name':tab[1],'group':tab[0],'type':'PE','left':os.path.abspath(tab[2]),'right':os.path.abspath(tab[3])})
	    else :
	        sys.stderr.write('not a good config file\n')
            if tab[0] not in data['group'] : data['group'].append(tab[0])
# start parse compare sheet
        if section == '[compare]' :
	    if len(tab) == 2:
	        data['compare'].append({'groupA':tab[0],'groupB':tab[1]})
	    else :
	        sys.stderr.write('not a good config file\n')
        if section == '[par]' :
	    if len(tab) == 2:
	        data['par'][tab[0]]=tab[1]
        if section == '[genome]' :
	    data['genome'] = tab[0]

    cf.close()
    return data

# check library config file for transcriptome pipeline
def check_cfg(cfg):
    ''' check cfg content only '''
    # check lib key 
    if not 'lib' in cfg or not cfg['lib'] :
	sys.stderr.write('no library config in file\n')
	return 0
    names = []
    groups= []
    # check attribute of lib key
    for l in cfg['lib'] :
	# check left file, must be specified
	if not 'left' in l :
	    sys.stderr.write('library must hvae file1\n')
	    return 0
	else:
	    # check access of left file
	    if not os.access(l['left'], os.R_OK) :
		sys.stderr.write('library file1 is not accessable\n')
		return 0
	if 'rigth' in l :
	    # is left file and right file same
	    if l['left'] == l['rigth'] :
		sys.stderr.write('library have same file1 and file2\n')
		return 0
	    # check access of right file
	    if not os.access(l['right'], os.R_OK) :
		sys.stderr.write('library file2 is not accessable\n')
		return 0

	# check type attribute
	if not 'type' in l :
	    sys.stderr.write('no library "type" config in file\n')
	    return 0
	else:
	    if l['type'] == 'SE' :
		if 'right' in l :
		    sys.stderr.write('library type is SE, but have two files\n')
		    return 0
	    else:
		if not 'right' in l :
		    sys.stderr.write('library type is PE, but no file2\n')
		    return 0
	# check name attribute
	if not 'name' in l :
	    sys.stderr.write('no library "name" config in file\n')
	    return 0
	else:
	    if not l['name'] in names :
		names.append(l['name'])
	    else:
		sys.stderr.write('library name '+l['name']+' duplicated\n')
		return 0
	# check group attribute
	if not 'group' in l :
	    sys.stderr.write('no library "group" config in file\n')
	    return 0
	else:
	    groups.append(l['group'])

    # chek compare key
    if 'compare' in cfg :
	for g in cfg['compare'] :
            (gA,gB) = (g['groupA'],g['groupB'])
	    if not gA in groups :
		sys.stderr.write('compare between '+gA+' and '+gB+', '+gA+' is not in library groups\n')
		return 0
	    if not gB in groups :
		sys.stderr.write('compare between '+gA+' and '+gB+', '+gB+' is not in library groups\n')
		return 0
    return 1
