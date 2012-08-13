# import abstract class Plugin
# from foldername.filename import classname
from modules.abstract import AbstractModule
from logger import Logger

# helper module
import helper
from logger import Logger

# standard modules
import json, collections
import os
import subprocess
import string

class Orca(AbstractModule):

	def __str__(self):
		return "Orca-Plugin"

	def info(self):
		"""
		returns a short describtion of the plugin
		"""
		return "Module to configure Orca"

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
		requirements['os'].append({"type":"linux","subtype":"debian","version":"6"})
		requirements['os'].append({"type":"linux","subtype":"ubuntu","version":"12.04"})
		return requirements

	def convert_values(self, attribute, value):
		if attribute == "preferred-lang":
			if value == "en":
				return {"name":"english-us", "locale":"en-us"}
			if value == "de":
				return {"name":"german", "locale":"de"}
		if attribute == "speech-rate":
			return {"rate":value}
		return None

	def setup(self, solution_name, settings):
		log = Logger()
		# first check if orca is installed
		orca_path = string.split(subprocess.check_output(["whereis", "orca"]), " ")
		if len(orca_path) <= 1:
			helper.speak_msg("Orca is not installed. I try to do this.  Please enter your sudo password in the following dialog.")
			print "Orca is not installed. I try to do this. Please enter your sudo password in the following dialog."
			while True:
				rc = subprocess.call(["sudo", "apt-get", "-y", "install", "gnome-orca", "speech-dispatcher"])
				if rc == 0:
					log.log_msg("Orca successfully installed.", "info", True)
					orca_path = string.split(subprocess.check_output(["whereis", "orca"]), " ")
					break
				if rc == 100:
					return 100
				if rc == 1:
					helper.speak_msg("Wrong password. Do you want to try again?	y/n")
					out = raw_input('Wrong password. Do you want to try again?	y/n: ')
					if out == "n":
						return 101
					else:
						continue
				return 102

		# next try to locate orca settings file		
		orca_settings_filename = os.environ['HOME'] + "/.local/share/orca/user-settings.conf"
		if os.path.exists(orca_settings_filename) == False:
			rc = subprocess.call([orca_path[1], "-t"])
			if rc > 0:
				return 103
			if os.path.exists(orca_settings_filename) == False:
				return 104
		orca_settings_file = open(orca_settings_filename,"r")
		orca_settings_string = orca_settings_file.read()
		try:
			orca_settings_json = json.loads(orca_settings_string, object_pairs_hook=collections.OrderedDict)
		except ValueError:
			return 105
		orca_settings_file.close()

		profile_name = "cloud4all"
		if orca_settings_json['profiles'].has_key(profile_name) == False:
			new_speech_profile = orca_settings_json['profiles']['default']
			orca_settings_json['profiles'][profile_name] = new_speech_profile
			orca_settings_file = open(orca_settings_filename,"w")
			orca_settings_file.write(json.dumps(orca_settings_json, sort_keys=False, indent=4))
			orca_settings_file.close()
			orca_settings_file = open(orca_settings_filename,"r")
			orca_settings_string = orca_settings_file.read()
			orca_settings_json = json.loads(orca_settings_string, object_pairs_hook=collections.OrderedDict)
			orca_settings_file.close()

		# general profile settings
		orca_settings_json['profiles'][profile_name]['profile'][0] = "Cloud4All"
		orca_settings_json['profiles'][profile_name]['profile'][1] = profile_name
		# make Cloud4All profile the active profile
		orca_settings_json['general']['startingProfile'][0] = "Cloud4All"
		orca_settings_json['general']['startingProfile'][1] = profile_name

		# apply user profile settings
		attrs_without_value = []
		for attr in self.get_solution_list()[solution_name]:
			if settings.has_key(attr) == True:
				value = self.convert_values(attr, settings[attr])
				if value == None:
					log.log_msg("Orca: The attribute " + attr + " couldn't be converted into a Orca specific format, skipped", "warning")
					continue
				if attr == "preferred-lang":
					try:
						orca_settings_json['profiles'][profile_name]['voices']['default']['family']['name'] = value['name']
						orca_settings_json['profiles'][profile_name]['voices']['default']['family']['locale'] = value['locale']
					except:
						log.log_msg("Orca: Error while changing the attribute " + attr + " in the Orca settings file.", "warning")
				if attr == "speech-rate":
					try:
						orca_settings_json['profiles'][profile_name]['voices']['default']['rate'] = value['rate']
					except:
						log.log_msg("Orca: Error while changing the attribute " + attr + " in the Orca settings file.", "warning")
			else:
				attrs_without_value.append(attr)

		# list of attributes without a corresponding value
		if len(attrs_without_value) > 0:
			attr_str = ""
			for attr in attrs_without_value:
				attr_str.join(attr)
			log.log_msg("Orca: The following supported attributes have no value in the user profile: " + attr_str, "warning")

		# write back the orca settings file
		try:
			orca_settings_file = open(orca_settings_filename,"w")
			orca_settings_file.write(json.dumps(orca_settings_json, sort_keys=False, indent=4))
			orca_settings_file.close()
		except:
			return 106


		if helper.is_process_running("orca") != "":
			rc = subprocess.call([orca_path[1], "-q"])
		os.system(orca_path[1] + " &")
		return 0

