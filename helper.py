# import abstract class Plugin
# from foldername.filename import classname
from modules.abstract import AbstractModule

import urllib2
import psutil
import os
import sys
import platform
from logger import Logger

def download_file(url, overwrite=False, print_output = False):
	file_name = url.split('/')[-1]
	if os.path.exists(file_name) == True and overwrite == False:
		return file_name
	
	try:
		u = urllib2.urlopen(url)
	except urllib2.HTTPError:
		return ""
	f = open(file_name, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	if print_output == True:
		print "Downloading: %s Bytes: %s" % (file_name, file_size)

	file_size_dl = 0
	block_sz = 8192
	while True:
		buffer = u.read(block_sz)
		if not buffer:
			break
		file_size_dl += len(buffer)
		f.write(buffer)
		status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
		status = status + chr(8)*(len(status)+1)
		if print_output == True:
			print status,

	f.close()
	return file_name


def is_process_running(searched_process_name):
	"""
	function checks if the given process is currently running
	if so it returns the path to the executable
	otherwise an empty string is returned
	"""
	searched_process_path = ""
	procs = psutil.get_process_list()
	for p in procs:
		try:
			if searched_process_name == p.name:
				searched_process_path = p.exe
				break
		except psutil.NoSuchProcess:
			procs.remove(p)
	return searched_process_path


def find_modules(path, cls):
	"""
	Find all subclass of cls in py files located below path
	(does look in sub directories)

	@param path: the path to the top level folder to walk
	@type path: str
	@param cls: the base class that all subclasses should inherit from
	@type cls: class
	@rtype: list
	@return: a list if classes that are subclasses of cls
	"""

	subclasses=[]

	def look_for_subclass(modulename):
		module=__import__(modulename)

		#walk the dictionaries to get to the last one
		d=module.__dict__
		for m in modulename.split('.')[1:]:
			d=d[m].__dict__

		#look through this dictionary for things
		#that are subclass of Job
		#but are not Job itself
		for key, entry in d.items():
			if key == cls.__name__:
				continue

			try:
				if issubclass(entry, cls):
					# print("Found subclass: "+key)
					subclasses.append(entry)
			except TypeError:
				#this happens when a non-type is passed in to issubclass. We
				#don't care as it can't be a subclass of Job if it isn't a
				#type
				continue

	for root, dirs, files in os.walk(path):
		# sort the files in the given directory
		sorted_files = []
		for filename in files:
			sorted_files.append(filename)
		sorted_files.sort()
		for name in sorted_files:
			if name.endswith(".py") and not name.startswith("__"):
				path = os.path.join(root, name)
				modulename = path.rsplit('.', 1)[0].replace('\\','.').replace('/', '.')
				look_for_subclass(modulename)

	return subclasses

def speak_msg(self, msg):
	# currently only supported for linux systems
	if platform.system() != "Linux":
		return 22
	audio_file = "/tmp/audio_command.wav"
	f = open(audio_file, 'w')
	cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		cSocket.connect(("localhost",2727))
	except socket.error:
		return 21
	cSocket.send(msg)
	while True:
		buffer = cSocket.recv(1024)
		f.write(buffer)
		if len(buffer) < 1024:
			break
	cSocket.close()
	f.close()
	subprocess.call(["aplay", audio_file])
	return 0

def print_by_error_code(rc):
	log = Logger()

	### helper class errors
	# 20 - 39
	# speak_msg:
	if rc == 21:
			log.log_msg("SpeakMSG: Audio output of messages currently not available for this os.", "warning")
	elif rc == 22:
		log.log_msg("SpeakMSG: Server for speech production not	available.", "warning")

	###### plugins
	# all error codes above 100
	### orca plugin
	# 100 - 199
	elif rc == 100:
		log.log_msg("Orca: The Orca package could not be found, maybe not available in this distibution", "error", True)
	elif rc == 101:
			log.log_msg("Orca: No admin previleges on this machine, Orca could not be installed.", "error", True)
	elif rc == 102:
		log.log_msg("Orca: Unknown error during Orca installation", "error", True)
	elif rc == 103:
		log.log_msg("Orca: Start of the Orca settings dialog was not successful", "error", True)
	elif rc == 104:
		log.log_msg("Orca: Although the Orca settings dialog ended successfully, there is still no settings file available", "error", True)
	elif rc == 105:
		log.log_msg("Orca: Json File is malformed.", "error", True)
	elif rc == 106:
		log.log_msg("Orca: Settings file couldn't be written", "error", True)

		### NVDA plugin
	# 200 - 299
	elif rc == 200:
		log.log_msg("NVDA: Downloader couldn't be loaded.", "error", True)
	elif rc == 201:
		log.log_msg("NVDA: Installation failed, maybe no admin privileges.", "error", True)
	elif rc == 202:
		log.log_msg("NVDA: Could not exit NVDA", "error", True)
	elif rc == 203:
		log = log_msg("NVDA: Config file not found." "error", True)
	elif rc == 204:
		log.log_msg("NVDA: settings file is malformed.", "error", True)
	elif rc == 205:
		log.log_msg("NVDA: Settings file couldn't be written", "error", True)
	else:
		log.log_msg("Unknown error code: ", "error")


