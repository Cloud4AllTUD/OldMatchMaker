# import abstract class Plugin
# from foldername.filename import classname
from modules.abstract import AbstractModule

# own classes
import helper
from device_profile import DeviceProfile
from logger import Logger

# standard modules
import json, collections
import httplib, urllib
import sys
import platform
import string
import os
#import logging


# possible sync solution between client and server
# zeromq (import zmq)
# http://stackoverflow.com/questions/7174478/background-process-in-python

def get_compatible_modules(device_profile, module_list):
	"""
	sort out the modules which don't match the requirements of the device
	profile
	"""
	compatible_module_list = []
	for dev_key,dev_attrs in zip(device_profile.keys(),device_profile.values()):
		for module in module_list:
			mod_req = module().get_requirements()
			if mod_req.has_key(dev_key) == True:
				for entry in mod_req[dev_key]:
					# compare the dict entrys of the device_profile and
					# the module, for example os
					compatible = True
					for k in dev_attrs:
						if not entry[k] in dev_attrs[k]:
							compatible = False
							break
					if compatible == True:
						compatible_module_list.append(module)
						break
	return compatible_module_list

def get_solutions(user_profile, module_list):
	solution_list = {}
	unknown_attributes = []
	found_attribute = False

	for entry in user_profile:
		# cut off the url part of the entry names in the user profile
		entry_name = string.split(entry['name'], "/")[-1]
		for module in module_list:
			sol_attr_touples = module().get_solution_list()
			for sol_name,attrs in zip(sol_attr_touples.keys(), sol_attr_touples.values()):
				if entry_name in attrs:
					if solution_list.has_key(sol_name) == False:
						solution_list[sol_name] = {module}
					else:
						solution_list[sol_name].add(module)
					found_attribute = True

		if found_attribute == False:
			unknown_attributes.append(entry_name)
		else:
			found_attribute = False

	print set(unknown_attributes)
	return solution_list


def get_settings_to_apply(attribute_list, user_profile):
	"""
	This function searches for the coresponding attribute values in the
	user profile
	the solution and the appropriate module are allready found 
	attribute_list: is a set and contains the attributes which the choosen
	module holds for configuration
	user_profile: the json style user profile
	returns a dict of the attributes with thair values, extracted from the
	user profile. This dictionary later can be transfered to the setup
	method of the chosen module
	"""
	attr_value_dict = {}
	attr_entry_dict = {}
	log = Logger()
	for attr in attribute_list:
		attr_entry_dict[attr] = []

	# collect all user profile entries which correspond to the attributes
	# in the given list
		for entry in user_profile:
			if attr in entry['name']:
				attr_entry_dict[attr].append(entry)

	# set the values for all attributes, which only have one entry in the
	# user profile
	for attr,entry_list in zip(attr_entry_dict.keys(),attr_entry_dict.values()):
		if len(entry_list) == 0:
			log.log_msg("SettingsToApply: The option " + attr + " was not found in the user profile, no value attached.", "warning")
		elif len(entry_list) == 1:
			attr_value_dict[attr] = entry_list[0]['value']

	entry_without_condition = None
	for attr,entry_list in zip(attr_entry_dict.keys(),attr_entry_dict.values()):
		if len(entry_list) > 1:
			for e in entry_list:
				if e['condition'] == "":
					entry_without_condition = e
				else:
					depents_on = resolve_up_setting_dependencies(e)
					if len(depents_on) == 0:
						continue
					if attr_value_dict.has_key(depents_on[1]) == True:
#						print attr_value_dict[depents_on], " = ", e['value']
						if attr_value_dict[depents_on[1]] == e['condition'][depents_on[0]]:
							attr_value_dict[attr] = e['value']
							break
# if the dependencies couldn't be resolved, use the standard
			# entry without conditions
			if attr_value_dict.has_key(attr) == False:
				if entry_without_condition == None:
					log.log_msg("GetSettingsForAttributeList: Dependencies couldn't be solved and there is no general entry for the " + attr + " option", "warning")
				else:
					attr_value_dict[attr] = entry_without_condition['value']
	return attr_value_dict


def resolve_up_setting_dependencies(entry):
	if type(entry) != type({}):
		return ""
	if entry.has_key('name') == False or entry.has_key('condition') == False:
		return ""
	for k in entry['condition'].keys():
		# self defined rules
		# a entry in the user profile with a defined condition depends on
		# another entry
		#
		# example: entry "speech-rate" with the "language" condition
		# depends on the value of preferred-lang, so the system can decide
		# if the speech-rate value with the condition or the common
		# speech-rate value should be used
		if "speech-rate" in  entry['name'] and k == "language":
			return ["language", "preferred-lang"]
	return ""

	
# here starts the main program
if __name__ == "__main__":
	log = Logger()
	log.set_log_level("info", "warning")
	# load modules
	imported_modules = helper.find_modules("modules", AbstractModule)
	# print the name of every found module
	print "Imported modules:"
	for i in range(len(imported_modules)):
		print imported_modules[i]()
	print"\n"

	while(1):
		# fetch json profile from server
		# download the profile file
		# the following if statement only belongs to my vm settings, if I
		# start the program under the host, the url is the localhost,
		# otherwise it's the given ip address
		file_name = ""
		if platform.node() == "scimitar":
			file_name =	helper.download_file("http://localhost/cloud4all/profile_json.txt",	True)
		else:
			file_name =	helper.download_file("http://10.0.2.2/cloud4all/profile_json.txt",	True)
		if os.path.exists(file_name) == False:
			log.log_msg("Error: Download of the profile file failed.", "error")
			sys.exit(1)
		f = open(file_name, "r")
		json_string = f.read()
		# parse the string
		try:
			user_profile = json.loads(json_string)
		except ValueError:
			log.log_msg("Error: Parsing of the user profile failed.", "error")
			sys.exit(2)

		dev_profile = DeviceProfile()
		compatible_modules = get_compatible_modules(dev_profile.get_device_profile(), imported_modules)
		c_modules = "compatible: ", compatible_modules
		log.log_msg(c_modules, "debug", False)
		solution_list = get_solutions(user_profile, compatible_modules)
		for s,m_set in zip(solution_list.keys(),solution_list.values()):
			module = m_set.__iter__().next()
			if len(m_set) > 1:
				print "More than one module is available for the ", s, "solution. At the moment the program chooses the first one	in the set"
			print "Configuring of the module", module().__str__()
			# get the values for the configurable options
			settings_to_apply = get_settings_to_apply(module().get_solution_list()[s], user_profile)
			print "settings: ", settings_to_apply
			rc = module().setup(s, settings_to_apply)
			rc = 0
			if rc == 0:
				print module().__str__(), "successfully configured"
			else:
				helper.print_by_error_code(rc)
		break


