__author__ = 'Nick'

from lana import Class

if __name__ == '__main__':
    c = Class()
    c.subject = 'MUTA'
    c.title = 'Advanced Mutation I'
    c.course = '414'
    c.section = '01'
    c.start_time = '9:00'
    c.instructor = 'Professor X'
    c.weekdays = 'MTF'
    c.end_time = '10:50'

    print(c)
