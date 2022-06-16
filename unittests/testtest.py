# -*- coding: utf-8 -*-
"""
Created on Wed Jun  16 14:49:46 2022

@author: ZechT
"""

#execute this file with "python testtest.py" in the console
#or use nose2 by typing in "python -m nose2" so you can filter all established unit tests inside this folder more effectively

from unittest import TestCase


class XXXClass(TestCase):
	#Collection of Testcases for a specific module or class
	#Testable attributes: Function, performance, interoperability
	
	def setUp(self):
		#declare test data
		self.parameter1 = 0
		self.parameter2 = [12,3441,123,4]
		self.parameter3 = 'TypeModule'
		#etc...
		
	def define_a_specific_case_that_should_be_tested_with_exact_description_in_the_name():
		pass
		#initialize the module to be tested and give it the necessary parameters
		#get the results from this module
		#check whether the result is identical to the expected value
		#example: self.assertEqual(Result,Assertion,"Error Message") #raises an assertion error which will be caught by the unittest framework

if __name__ == "__main__":
	unittest.main()
	
	