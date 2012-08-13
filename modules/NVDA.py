# import abstract class Plugin
# from foldername.filename import classname
from modules.abstract import AbstractModule
from logger import Logger

import os
import helper
import subprocess
from configobj import ConfigObj

class NVDA(AbstractModule):

	def __str__(self):
		return "NVDA-Plugin"

	def info(self):
		"""
		returns a short describtion of the plugin
		"""
		return "Module to configure the NVDA screen reader under Windows"

	def get_solution_list(self):
		"""
		returns a list containing all solutions which this plugin implements
		a solution is defined as a dict object
		the keys are the solution names e.x. "screen-reader"
		the values are grouped in a set and define the supported attributes
		for the given solution
		"""
		solution_list = {}
		# add screen reader solution
		solution_list["screen-reader"] = {"preferred-lang","speech-rate"}
		return solution_list

	def get_requirements(self):
		"""
		returns a dict ofrequirements
		keys are the option names like "os"
		values describe the keys and orientate them on the device profile
		settings
		"""
		requirements = {}
		# add supported os
		requirements['os'] = []
		requirements['os'].append({"type":"windows","subtype":"","version":"xp"})
		return requirements

	def convert_values(self, attribute, value):
		if attribute == "preferred-lang":
			if value == "en":
				return { "voice":"en\\en-us" }
			if value == "de":
				return { "voice":"de" }
		if attribute == "speech-rate":
			return { "rate":value, "rateBoost":False }
		return None


	def setup(self, solution_name, settings):
		log = Logger()
		# check if nvda is allready installed on the system, if not, install it
		standard_nvda_path = "C:\\Programme\\NVDA\\nvda.exe"
		nvda_path = helper.is_process_running("nvda.exe")
		if nvda_path == "":
			nvda_path = standard_nvda_path
		
		if os.path.exists(nvda_path) == False:
			# nvda download url
			url = "http://downloads.sourceforge.net/project/nvda/releases/2012.2.1/nvda_2012.2.1.exe"
			# download nvda installer
			nvda_installer = helper.download_file(url)
			if nvda_installer == "":
				return 200
			# install nvda
			rc = subprocess.call([nvda_installer, "--install"])
			if rc > 0:
				return 201
		# if nvda runs, exit it
		nvda_path = helper.is_process_running("nvda.exe")
		if nvda_path != "":
			rc = subprocess.call([nvda_path, "-q"])
			if rc > 0:
				return 202
		else:
			nvda_path = standard_nvda_path
		
		# configure the program and start it
		config_file = os.environ['APPDATA'] + "\\nvda\\nvda.ini"
		if os.path.exists(config_file) == False:
			return 203
	
		# parse the ini config file
		try:
			config = ConfigObj(config_file)
		except configobj.ParseError:
			return 204


		# apply the settings
		attrs_without_value = []
		for attr in self.get_solution_list()[solution_name]:
			if settings.has_key(attr) == True:
				value = self.convert_values(attr, settings[attr])
				if value == None:
					log.log_msg("NVDA: The attribute " + attr + " couldn't be converted into a NVDA specific format, skipped", "warning")
					continue
				if attr == "preferred-lang":
					try:
						config['speech']['espeak']['voice'] = value['voice']
					except:
						log.log_msg("NVDA: Error while changing the attribute " + attr + " in the NVDA settings file.", "warning")
				if attr == "speech-rate":
					try:
						config['speech']['espeak']['rate'] = value['rate']
						config['speech']['espeak']['rateBoost'] = value['rateBoost']
					except:
						log.log_msg("NVDA: Error while changing the attribute " + attr + " in the NVDA settings file.", "warning")
			else:
				attrs_without_value.append(attr)

		# list of attributes without a corresponding value
		if len(attrs_without_value) > 0:
			attr_str = ""
			for attr in attrs_without_value:
				attr_str.join(attr)
			log.log_msg("NVDA: The following supported attributes have no value in the user profile: " + attr_str, "warning")

		# write back the nvda settings file
		try:
			config.write()
		except:
			return 205

		# start configured nvda
		rc = os.popen(nvda_path)
#		rc = os.system(nvda_path + " &")
		print "start nvda, rc = ", rc
		return 0

