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

from bea.pages.cohort_pages import CohortPages
from bea.pages.list_view_student_pages import ListViewStudentPages
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


class CohortAndGroupStudentPages(CohortPages, ListViewStudentPages):
    CONFIRM_EXPORT_LIST_BUTTON = By.ID, 'export-list-confirm'
    NO_ACCESS_MSG = By.XPATH, '//span[text()="You are unauthorized to access student data managed by other departments"]'
    TITLE_REQUIRED_MSG = By.XPATH, '//span[text()="Required"]'

    def confirm_export(self, cohort):
        self.wait_for_element_and_click(self.CONFIRM_EXPORT_LIST_BUTTON)

    def export_default_student_list(self, cohort):
        app.logger.info('Exporting student list with default columns')
        utils.prepare_download_dir()
        self.click_export_list()
        self.confirm_export(cohort)
        return utils.wait_for_export_csv()

    def export_custom_student_list(self, cohort):
        app.logger.info('Exporting student list with default columns')
        utils.prepare_download_dir()
        self.click_export_list()
        for i in range(19):
            self.wait_for_element_and_click((By.ID, f'csv-column-options-{i}'))
        self.confirm_export(cohort)
        return utils.wait_for_export_csv()

    @staticmethod
    def verify_default_export_student_list(cohort, csv_reader):
        sids = []
        first_names = []
        last_names = []
        emails = []
        phones = []
        for r in csv_reader:
            sids.append(r['sid'])
            first_names.append(r['first_name'])
            last_names.append(r['last_name'])
            emails.append(r['email'])
            phones.append(r['phone'])
        sids.sort()
        cohort_sids = list(map(lambda m: m.sid, cohort.members))
        cohort_sids.sort()
        assert sids == cohort_sids
        assert list(filter(lambda fi: fi, first_names))
        assert list(filter(lambda la: la, last_names))
        assert list(filter(lambda em: em, emails))
        assert list(filter(lambda ph: ph, phones))

    @staticmethod
    def verify_custom_export_student_list(cohort, csv_reader):
        prev_term_sis_id = utils.get_prev_term_sis_id()
        prev_prev_term_sis_id = utils.get_prev_term_sis_id(prev_term_sis_id)
        majors = []
        minors = []
        subplans = []
        levels_by_units = []
        terms_in_attend = []
        expected_grad_terms = []
        units_complete = []
        gpas_last_term = []
        gpas_last_last_term = []
        cumul_gpas = []
        program_statuses = []
        transfers = []
        intended_majors = []
        units_in_progress = []
        for r in csv_reader:
            majors.append(r['majors'])
            minors.append(r['minors'])
            subplans.append(r['subplans'])
            levels_by_units.append(r['level_by_units'])
            terms_in_attend.append(r['terms_in_attendance'])
            expected_grad_terms.append(r['expected_graduation_term'])
            units_complete.append(r['units_completed'])
            gpas_last_term.append(r[f'term_gpa_{prev_term_sis_id}'])
            gpas_last_last_term.append(r[f'term_gpa_{prev_prev_term_sis_id}'])
            cumul_gpas.append(r['cumulative_gpa'])
            program_statuses.append(r['program_status'])
            transfers.append(r['transfer'])
            intended_majors.append(r['intended_major'])
            units_in_progress.append(r['units_in_progress'])
        assert list(filter(lambda ma: ma, majors))
        assert list(filter(lambda mi: mi, minors))
        assert list(filter(lambda su: su, subplans))
        assert list(filter(lambda le: le, levels_by_units))
        assert list(filter(lambda te: te, terms_in_attend))
        assert list(filter(lambda ex: ex, expected_grad_terms))
        assert list(filter(lambda uc: uc, units_complete))
        assert list(filter(lambda gpl: gpl, gpas_last_term))
        assert list(filter(lambda gpll: gpll, gpas_last_last_term))
        assert list(filter(lambda cu: cu, cumul_gpas))
        assert list(filter(lambda pr: pr, program_statuses))
        assert list(filter(lambda tr: tr, transfers))
        assert list(filter(lambda ima: ima, intended_majors))
        assert list(filter(lambda up: up, units_in_progress))

    # LIST VIEW - shared by filtered cohorts and curated groups

    TERM_SELECT = By.ID, 'students-term-select'
    SITE_ACTIVITY_HEADER = By.XPATH, '//th[contains(., "bCourses Activity")]'

    def select_term(self, term_sis_id):
        app.logger.info(f'Selecting term ID {term_sis_id}')
        self.wait_for_select_and_click_option(self.TERM_SELECT, term_sis_id)
        self.wait_for_spinner()

    def selected_term_sis_id(self):
        select = Select(self.element(self.TERM_SELECT))
        option = select.first_selected_option
        return option.get_attribute('value')

    def scroll_to_student(self, student):
        self.scroll_to_element(self.element((By.XPATH, self.student_row_xpath(student))))

    # Per student data

    def academic_standing(self, student):
        loc = By.XPATH, f'//span[contains(@id, "student-{student.sid}-academic-standing")]'
        return self.el_text_if_exists(loc)

    def classes(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//span[contains(@id, "student-enrollment-name")]'
        return list(map(lambda cl: cl.text, self.elements(loc)))

    def cumulative_units(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//div[contains(@id, "cumulative-units")]'
        return self.el_text_if_exists(loc, 'No data')

    def cxl_msg(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//div[contains(@id, "withdrawal-cancel")]'
        return self.el_text_if_exists(loc)

    def entered_term(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//div[contains(@id, "student-matriculation")]'
        return self.el_text_if_exists(loc, 'Entered')

    def gpa(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//span[contains(@id, "student-cumulative-gpa")]'
        return self.el_text_if_exists(loc, 'No data')

    def grad_term(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//div[contains(@id, "student-grad-term")]'
        return self.element(loc).text.split(':')[1].strip() if self.is_present(loc) else None

    def graduation(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//div[starts-with(text(), " Graduated")]'
        return self.el_text_if_exists(loc, 'Graduated')

    def inactive_flag(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//div[contains(@id, "-inactive")]'
        return self.is_present(loc) and self.element(loc).text.strip() == 'INACTIVE'

    def level(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//div[contains(@id, "student-level")]'
        return self.el_text_if_exists(loc)

    def majors(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//span[contains(@id, "student-major")]'
        return self.els_text_if_exist(loc)

    def sports(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//span[contains(@id, "student-team")]'
        return self.els_text_if_exist(loc)

    def term_units(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//div[contains(@id, "student-enrolled-units")]'
        return self.el_text_if_exists(loc)

    def term_units_max(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//span[contains(@id, "student-max-units")]'
        return self.el_text_if_exists(loc)

    def term_units_min(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//div[contains(@id, "student-min-units")]'
        return self.el_text_if_exists(loc)

    def course_row_xpath(self, student, course_idx):
        return f'{self.student_row_xpath(student)}//tbody/tr[{course_idx + 1}]'

    def course_code(self, student, course_idx):
        return self.el_text_if_exists((By.XPATH, f'{self.course_row_xpath(student, course_idx)}/td[1]'), '(W)\nWaitlisted')

    def course_units(self, student, course_idx):
        return self.el_text_if_exists((By.XPATH, f'{self.course_row_xpath(student, course_idx)}/td[2]'))

    def course_activity(self, student, course_idx):
        return self.el_text_if_exists((By.XPATH, f'{self.course_row_xpath(student, course_idx)}/td[3]'), 'No data')

    def course_mid_grade(self, student, course_idx):
        return self.el_text_if_exists((By.XPATH, f'{self.course_row_xpath(student, course_idx)}/td[4]'), 'No data')

    def is_course_mid_flagged(self, student, course_idx):
        xpath = f'{self.course_row_xpath(student, course_idx)}/td[4]//i[contains(@class, "text-warning")]'
        return self.is_present((By.XPATH, xpath))

    def course_final_grade(self, student, course_idx):
        return self.el_text_if_exists((By.XPATH, f'{self.course_row_xpath(student, course_idx)}/td[5]'))

    def is_course_final_flagged(self, student, course_idx):
        xpath = f'{self.course_row_xpath(student, course_idx)}/td[5]//i[contains(@class, "text-warning")]'
        return self.is_present((By.XPATH, xpath))

    def wait_lists(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//span[contains(@id, "-waitlisted-")]/preceding-sibling::span'
        return list(map(lambda wa: wa.text, self.elements(loc)))

    # SORTING

    def sort_by_team(self):
        self.sort_by('group_name')

    def sort_by_gpa_cumulative(self):
        self.sort_by('gpa')

    def sort_by_gpa_cumulative_desc(self):
        self.sort_by('gpa desc')

    def sort_by_last_term_gpa(self, term=None):
        term = term or utils.get_previous_term()
        self.sort_by(f'term_gpa_{term.sis_id}')

    def sort_by_last_term_gpa_desc(self, term=None):
        term = term or utils.get_previous_term()
        self.sort_by(f'term_gpa_{term.sis_id} desc')

    def sort_by_level(self):
        self.sort_by('level')

    def sort_by_student_major(self):
        self.sort_by('major')

    def sort_by_entering_term(self):
        self.sort_by('entering_term')

    def sort_by_expected_graduation(self):
        self.sort_by('expected_grad_term')

    def sort_by_terms_in_attend(self):
        self.sort_by('terms_in_attendance')

    def sort_by_terms_in_attend_desc(self):
        self.sort_by('terms_in_attendance desc')

    def sort_by_units_in_progress(self):
        self.sort_by('enrolled_units')

    def sort_by_units_in_progress_desc(self):
        self.sort_by('enrolled_units desc')

    def sort_by_units_completed(self):
        self.sort_by('units')

    def sort_by_units_completed_desc(self):
        self.sort_by('units desc')
