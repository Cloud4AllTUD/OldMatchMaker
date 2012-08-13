# this class creates a simple device profile of the current running machine
# it also can export this profile to a json file

import platform
import json, collections
import string

class DeviceProfile():
	device_profile = {}

	def __init__(self):
		# get current operating system
		if platform.system() == "Linux":
			os_ver = platform.dist()
			self.device_profile['os'] = {"type":"linux","subtype":string.lower(os_ver[0]),"version":string.lower(os_ver[1])}
		elif platform.system() == "Windows":
			os_ver = platform.win32_ver()
			self.device_profile['os'] = {"type":"windows","subtype":"","version":string.lower(os_ver[0])}
		else:
			self.device_profile['os'] = {"type":"other","subtype":"","version":""}

	def get_device_profile(self):
		return self.device_profile

	def export_to_json(self):
		"""
		this function creates a json file from the device_profile variable
		return codes:
			0: creation was successful
			1: file could not be created
			2: device_profile var is malformed
		"""
		try:
			file_contents = json.dumps(self.device_profile, indent=4)
		except SyntaxError:
			print "Error in Json serialization"
			return 1

		try:
			f = open("device_profile.txt","w")
		except IOError:
			print "Could not create file"
			return 2

		f.write(file_contents)
		f.close()
		return 0

if __name__ == '__main__':
	dp = DeviceProfile()
	print dp.get_device_profile()
	dp.export_to_json()
