#
# Contains an encapsulation of class data for the schedules
# This should not be abstracted as it is already in a final mode
# The data for this class should be parsed by the individual
#  modules, and should be represented as a global class
#

class Class():
	'''
	A class to encapsulate all kinds of class data
	This should be in a global form, so all modules should end up
	 with the same data.
	
	'''
	
	subject = ''			# Ex: 'COMP'
	course = ''				# Ex: '285'
	section = ''			# Ex '09'
	credits = 0.00			# Ex: 4.00
	start_time = 0000		# 24 hour time
	end_time = 0000			# 24 hour time
	start_date = ()			# Ex: 8, 29		Month, Day
	end_date = ()			# Ex: 12, 3		Month, Day
	weekdays = []			# MTWRFSU
	title = ''				# Ex: 'Object Oriented Programming'
	instructor = ''			# Ex: 'Michael Werner'
	class_max = 0			# How many students can be in the class
	class_cur = 0			# How many students ARE in the class
	location = ''			# Ex: ANNXC 102
	campus = ''				# Ex: 'WIT'
	
	# Select few have something like this:
	crn = ''				# Course registration number
	
	# Other stuff this may have missed
	misc = ''

	def __init__( self ):
		pass
