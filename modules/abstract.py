#!/usr/bin/env python

class AbstractModule(object):
	""" abstract module class """

	def info(self):
		raise NotImplementedError

	def get_solution_list(self):
		raise NotImplementedError

	def get_requirements(self):
		raise NotImplementedError

	def setup(self, solution_name, settings):
		raise NotImplementedError
