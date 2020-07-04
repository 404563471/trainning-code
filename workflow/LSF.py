# package LSF;
# by Yan Pengcheng yanpc@bcc.ac.cn
# Perl module for LSF on BCC cluster
# Program Version 1.0    2013-01-15

import os
import re
import os.path
import sys
import time
import commands
from Shell import *

class LSF:
    """ LSF module for BCC cluster
    """

    my_queue = 'bioblade'

    def __init__(self, cmd, cpu, job, queue):

	if not queue : self._queue = self.my_queue
	else: self._queue = queue

	if not job : self._job = 'IN-job'
	else : self._job = job

	self._logger = logging.getLogger('CMD')

	self._cmd = cmd
	match = re.search(r'(\d+):(\d+)', cpu)
	if match :
	    node = match.group(1)
	    core = match.group(2)
	    self._cpu = int(core) * int(node)
	    self._node = node
	    self._core = core
	else: self._cpu = 1
	self._jid = '0'
	self._job_status = 1

    def submit_job(self):
	""" method to submit job
	"""

	os.environ['LSF_FROM_WEB'] = 'Y'

	if self._node == '1' and self._cpu > 1 :
	    # for OMP job
	    os.environ['OMP_NUM_THREADS'] = self._core
	    bsub = 'bsub -R "span[ptile='+self._core+']" -q '+self._queue+' -n '+self._core+' -J '+self._job+' -oo output.%J "'+self._cmd+'"'
	else:
	    bsub = 'bsub -q '+self._queue+' -n '+str(self._cpu)+' -J '+self._job+' -oo output.%J "'+self._cmd+'"'

	self._logger.debug(bsub)
	(stat,out) = commands.getstatusoutput(bsub)
	if stat :
	    self._logger.error('Submit job ['+self._job+'] fialed\n')
	else:
	    match = re.search(r'.*<(\d+)>', out)
	    if match :
		self._jid = match.group(1)
		#sys.stderr.write('Job '+self._job+' is submited as [ '+ self._jid +' ]\n')
	    else:
		self._logger.error('Cannot match job id\n')
		stat = 1

	os.environ['LSF_FROM_WEB'] = ''
	return stat

    def job_stat(self):
	""" method to get job stat
	"""
	#self._job_status = 1
	(status,out) = commands.getstatusoutput('bjobs -d ' + self._jid)
	if status :
	    sys.stderr.write('Submit job ['+self._job+'] fialed\n')

	regex = self._jid+'\s+.*?\s+(.*?)\s+'
	match = re.search(regex,out)
	if match :
	    stat_msg = match.group(1)
	    if stat_msg == "RUN" or stat_msg == "PEND":
		self._job_status = 1
	    elif stat_msg == 'DONE':
		self._job_status = 0
		#sys.stderr.write('Job '+self._jid+' is Done\n')
	    else:
		self._job_status = -1
		self._logger.error('Job '+self._jid+' is '+stat_msg+', please check it manually\n')
	else:
	    self._job_status = -2
	    self._logger.error('Job '+self._jid+' is lost in LSF system, please check it manually\n')

	return self._job_status

    def wait_job(self):
	""" wait job done"""

	while(1 == self._job_status):
	    self.job_stat()
	    time.sleep(180)

	return self._job_status

