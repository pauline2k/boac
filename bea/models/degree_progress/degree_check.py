"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""
import copy

from bea.models.degree_progress.degree_check_template import DegreeCheckTemplate
from bea.models.degree_progress.degree_completed_course import DegreeCompletedCourse


class DegreeCheck(DegreeCheckTemplate):

    def __init__(self, data, template, student):
        super().__init__(data)
        self.template = template
        self.categories = copy.deepcopy(self.template.categories)
        self.name = copy.deepcopy(self.template.name)
        self.student = student
        self.unit_reqts = copy.deepcopy(self.template.unit_reqts)

        for req in self.unit_reqts:
            req.units_completed = 0

        for cat in self.categories:
            for course in cat.course_reqts:
                if course.is_transfer_course:
                    cat_transfer = self.generate_transfer_course(course)
                    self.completed_courses.append(cat_transfer)
            for sub_cat in cat.sub_categories:
                for sub_course in sub_cat.course_reqts:
                    if sub_course.is_transfer_course:
                        sub_cat_transfer = self.generate_transfer_course(sub_course)
                        self.completed_courses.append(sub_cat_transfer)

    @property
    def check_id(self):
        return self.data.get('check_id')

    @check_id.setter
    def check_id(self, value):
        self.data['check_id'] = value

    @property
    def completed_courses(self):
        return self.data.get('completed_courses') or []

    @completed_courses.setter
    def completed_courses(self, value):
        self.data['completed_courses'] = value

    @property
    def note(self):
        return self.data.get('note')

    @note.setter
    def note(self, value):
        self.data['note'] = value

    @property
    def student(self):
        return self.data.get('student')

    @student.setter
    def student(self, value):
        self.data['student'] = value

    @staticmethod
    def generate_transfer_course(course_reqt):
        course = DegreeCompletedCourse({
            'grade': 'T',
            'manual': True,
            'name': course_reqt.name,
            'transfer_course': True,
            'units': course_reqt.units,
            'unit_reqts': course_reqt.unit_reqts,
        })
        course_reqt.completed_course = course
        course.course_reqt = course_reqt
        return course
