#
# Contains an encapsulation of class data for the schedules
# This should not be abstracted as it is already in a final mode
# The data for this class should be parsed by the individual
#  modules, and should be represented as a global class
#

from lana.utils import class2json


@DeprecationWarning
class Class():
    """ A class to encapsulate all kinds of class data
    This should be in a global form, so all modules should end up
    with the same data.
    """

    subject = ''  # Ex: 'COMP'
    course = ''  # Ex: '285'
    section = ''  # Ex '09'
    title = ''  # Ex: 'Object Oriented Programming'
    credits = 0.00  # Ex: 4.00
    start_time = ''  # 24 hours string, ex: '9:50'
    end_time = ''  # 24 hours string, ex: '17:50'
    start_date = ''  # Ex: '5/29' Month, Day
    end_date = ''  # Ex: '12/5'     Month, Day
    weekdays = ''  # MTWRF
    instructor = ''  # Ex: 'Michael Werner'
    class_max = 0  # How many students can be in the class
    class_cur = 0  # How many students ARE in the class
    location = ''  # Ex: ANNXC 102
    campus = ''  # Ex: 'WIT'

    # Select few have something like this:
    crn = ''  # Course registration number

    # Other stuff this may have missed
    misc = ''

    def __init__(self):
        pass

    def json(self, stringify=False):
        return class2json(self, stringify)

    def __str__(self):
        s = ''
        s += self.subject + ' '
        s += self.course

        if self.section:
            s += '-' + self.section

        if self.title:
            s += ' - ' + self.title + ' '

        if self.instructor:
            s += 'with ' + self.instructor + ' '

        if self.weekdays:
            s += 'every ' + self.weekdays + ' '

        if self.start_date:
            s += 'from ' + self.start_date + ' '

        if self.start_time:
            s += 'at ' + self.start_time + ' '

        if self.end_time:
            s += 'to ' + self.end_time + ' '

        if self.end_date:
            s += 'through ' + self.end_date + ' '

        if self.credits:
            s += 'worth ' + str(self.credits) + ' credits '

        if self.location:
            s += 'located at ' + self.location + ' '

        if self.campus:
            s += 'on ' + self.campus

        return s
