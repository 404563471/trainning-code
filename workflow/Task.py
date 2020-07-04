# package Task
# by Yan Pengcheng yanpc@bcc.ac.cn
# Python module for LSF on BCC cluster
# Program Version 1.1    2014-09-12

import re
import os
import os.path
import sys
import time
import logging
from string import Template
#from Shell import *
import Shell
import LSF

class Task:
    """ task module """

    job_system = 'LSF' # can be NULL, LSF, PBS, SGE
    job_queue  = 'bioblade'#normal' #bioloong' # job queue for LSF
    message = ''
    id = 0

    def __init__(self, dict):
	""" init parameters """
	
	self._err = 0
	self._dry_run = 0
	self._job_system = self.job_system
	self._dict = dict
	self._status = ''    # skip, running, error or done
	self._taskid = 0
	self._logger = logging.getLogger('TASK')

	if self.task_check() > 0 :
	    self._status = 'error'
	else:
	    tmpl = Template(self._dict['CMD']).safe_substitute(self._dict['INPUT'])
	    self._dict['CMD'] = Template(tmpl).safe_substitute(self._dict['OUTPUT'])
	    self._name = self._dict['NAME']

	    if self.uptodate(self._dict['INPUT'].values(), self._dict['OUTPUT'].values()) :
		self._logger.info('Step '+self._name+' ... skiped')
		self._status = 'skip'    # mark task status done

	    self.task_start()

    def task_check(self):
	""" check task parameters """

	if not 'PWD' in self._dict or not self._dict['PWD']: self._dict['PWD'] = './'
	if not 'NAME' in self._dict or not self._dict['NAME']: self._dict['NAME'] = 'bioCompute'
	if not 'DESC' in self._dict : self._dict['DESC'] = 'NULL'
	if not os.path.exists(self._dict['PWD']) :
	    try:
		os.makedirs(self._dict['PWD'])
	    except:
		self._logger.error( "Can't make Working dir, please check if have proper permission\n")

	if not 'CMD' in self._dict :
	    self._logger.error('No CMD can be found\n')
	    self._err+=1

	if 'INPUT' not in self._dict or len(self._dict['INPUT']) <= 0 :
	    self._logger.error('No INPUT can be found\n')
	    self._err+=1

	if 'OUTPUT' not in self._dict or len(self._dict['OUTPUT']) <= 0 :
	    self._logger.error('No OUTPUT can be found\n')
	    self._err+=1

	if not 'TYPE' in self._dict or len(self._dict['TYPE']) < 3 :
	    self._logger.error('TYPE value has error\n')
	    self._err+=1
	
	return self._err

    def task_start(self):
	"""
	run task
	submit task to job management system
	run task accouding to configuration
	"""

	if self._status != '' : return 0

	pwd    = self._dict['PWD']
	cwd    = os.getcwd()
	cmd    = self._dict['CMD']
	(type,source) = self._dict['TYPE'].split(':',1)

	try:
	    os.chdir(pwd)
	except:
	    self._logger.error("Change working dir failed\n")

	if self._dry_run:
	    self._status = 'done'
	else:
	    #if self._job_system == 'NULL':
	    if type == 'SYS':
			self._taskid = Shell.Shell()
			self._taskid.run_shell(cmd)
	    else:
			self._taskid = LSF.LSF(cmd,source,self._name,self.job_queue)
            self._taskid.submit_job()
            self._logger.info('Step '+self._name+' start, '+ self._dict['DESC'] )
            self._logger.info('cd '+ self._dict['PWD'] )
            self._logger.info(self._dict['CMD'] )
            self._logger.info('cd ' + cwd )
            self._status = 'running'

	    if self._taskid == -1 :
            self._logger.error('Step '+self._name+' submit JMS job failed')
            self._status = 'error'
	try:
	    os.chdir(cwd)
	except:
	    self._logger.error("Change working dir failed\n")
	

    def task_till_end(self):
	"""
	wait task to end
	wait shell task to end
	"""

	(type,source) = self._dict['TYPE'].split(':',1)
	job_status = 0

	if self._status == 'skip' : return 0
	if self._dry_run :
	    self._logger.info('Step '+self._name+' ... [Not run] done')
	    return 0

	if self._status == 'running' :
		#if self._job_system == 'NULL':
	    if type == 'SYS':
		    job_status = self._taskid.wait_shell_job()
	    else:
		    job_status = self._taskid.wait_job()
	    if job_status == 0 :
	        self._status = 'done'
	    else:
	        self._status = 'error'

	self._logger.info('Step '+self._name+' ... [job:'+str(self._taskid._jid)+'] '+self._status)


    def task_status(self):
	""" update task status """

	if self._status == 'skip' : return 0
	if self._status == 'error' : return 0
	if self._status == 'done' : return 0

	if self._dry_run : return 0

	(type,source) = self._dict['TYPE'].split(':',1)
	job_status = 1

	if type == 'SYS':
	    job_status = self._taskid.shell_job_stat()
	else:
	    job_status = self._taskid.job_stat()

	if job_status < 0 :
	    self._status = 'error'
	elif job_status == 0:
	    self._status = 'done'
	    self.task_till_end()
	else:
	    self._status = 'running'

	return job_status


    def task_clean(self):
	""" clean task files """

	if self._status == 'skip' : return 0
	if self._status == 'running' : return 0
        if not 'OUTPUT' in self._dict : return 0

	if not self._dry_run:
	    os.system('rm -f '+' '.join(self._dict['OUTPUT'].values()))


###################################################################################
# uptodate
# check whether output files are up to date with respect to input files
# all output files must exist and not be older than any input file
###################################################################################

    def uptodate(self, input, output):
	""" input : list of input file names
	    output : list of input file names
	    0 means need to update
	    1 means to skip
	"""

	earliestOutMtime = 0	# earliest modification time of an output file
	latestInMtime = 0	# latest modification time an any input file
	stat_list = ()		# holds info about file

	if len(input) == 0: return 0 # no input is always older than output files
	# check existence and times of input files
	for f in input :
	    if not os.path.exists(f) : # ignore if input file does not exist
		sys.stderr.write('Warning: '+f+' missing.\n') # TODO, remove or correct this later
		return 1

	    stat_list = os.stat(f)
	    if not latestInMtime or stat_list[9] > latestInMtime :
		latestInMtime = stat_list[9]

	if len(output) == 0 : return 0 # no output is always up to date
	# check whether all output files exist
	for f in output :
	    if not os.path.exists(f) : return 0 # if output file does not exist, up to data
	    stat_list = os.stat(f)
	    if not earliestOutMtime or stat_list[9] < earliestOutMtime :
		earliestOutMtime = stat_list[9]

	return (latestInMtime <= earliestOutMtime)
