# package Shell;
# by Yan Pengcheng yanpc@bcc.ac.cn
# Perl module for PBS on CMB cluster
# Program Version 1.0    2013-01-03

import sys
import os
import errno
import logging
import commands
import subprocess
from multiprocessing import Process

class Shell:
    """ shell module for unix
    """

    def __init__(self):
	self._start = 0
	self._end = 1
	self._job_status = 1
	#self._pid = 0
	self._logger = logging.getLogger('BASH')


    def run_shell(self, cmd):
	""" method to run shell command """
	status = 1
	try:
	    status = subprocess.call(cmd,shell=True)#commands.getstatusoutput(cmd)
	    #(status, output) = commands.getstatusoutput(cmd)
	    if status != 0:
		self._logger.error("Couldn't run : "+cmd+", please check it manually\n")
	    #sys.stderr.write(output)

	except OSError,o:
	    if o.errno == errno.ENOTDIR or o.errno == errno.ENOENT:
		self._logger.error("Couldn't found : "+cmd+", please check it manually\n")
	    self._logger.debug(str(status))

	return status

    def submit_shell_job(self, cmd):
	""" method to submit backgroud shell command """

	# submit background shell!
	try:
	    self._job = Process(target=self.run_shell, args=(cmd,))
	    self._job.start()
	    self._jid = self._job.pid()
	except:
	    self._jid = 0
	    self._logger.error("Fork process failed!\n")

	return self._jid

    def wait_shell_job(self):
	""" method to wait shell job """

	try:
	    self._job.join()
	except:
	    self.logger.error('child process is lost\n')
	return 0

    def shell_job_stat(self):
	""" method to get job stat
	"""
	if self._job.is_alive() :
	    self._job_status = 1
	else:
	    self._job_status = self._job.exitcode
	    #self._job_status = -2
	return self._job_status
