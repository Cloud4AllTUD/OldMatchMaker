import logging
import socket
import subprocess
import helper

class Borg:
	_shared_state = {}
	def __init__(self):
		self.__dict__ = self._shared_state

class Logger(Borg):
	logger = None

	def __init__(self):
		Borg.__init__(self)
	
	def set_log_level(self, screen_log_level, file_log_level):
		self.logger = logging.getLogger()
		self.logger.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

		fh = logging.FileHandler('log_file.txt')
		fh.setFormatter(formatter)
		fh.setLevel(logging.WARNING)
		self.logger.addHandler(fh)

		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		self.logger.addHandler(ch)

#		self.logger.handlers[0].setLevel(logging.WARNING)
#		self.logger.handlers[1].setLevel(logging.INFO)

	def log_msg(self, msg, level="info", speech=False):
		if speech == True:
			rc = helper.speak_msg(msg)
			if rc > 0:
				helper.print_by_error_code(rc)
		if level == "debug":
			self.logger.debug(msg)
		elif level == "info":
			self.logger.info(msg)
		elif level == "warning":
			self.logger.warning(msg)
		elif level == "error":
			self.logger.error(msg)
		else:
			self.logger.critical(msg)

