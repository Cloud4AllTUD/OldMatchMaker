# import abstract class Plugin
# from foldername.filename import classname
from modules.abstract import AbstractModule

class FontSize(AbstractModule):

	def __str__(self):
		return "FontSize-Plugin"


	def info(self):
		"""
		returns a short describtion of the plugin
		"""
		return "Module to configure the font size"


	def get_solution_list(self):
		"""
		returns a list containing all solutions which this plugin implements
		a solution is defined as a dict object
		the keys are the solution names e.x. "screen-reader"
		the values are grouped in a set and define the supported attributes
		for the given solution
		"""
		solution_list = {}
		# add font size solution
		solution_list["font-size"] = {"preferred-font-size"}
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
		requirements['os'].append({"type":"windows","subtype":"","version":"xp"})
		return requirements


	def setup(self, solution_name, settings):
		# no implementation yet
		# just a dummy plugin
		return 0

