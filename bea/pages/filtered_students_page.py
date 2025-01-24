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

from bea.pages.cohort_and_group_student_pages import CohortAndGroupStudentPages
from bea.pages.curated_add_selector import CuratedAddSelector
from bea.pages.curated_modal import CuratedModal
from bea.pages.filtered_students_page_filters import FilteredStudentsPageFilters
from bea.pages.filtered_students_page_results import FilteredStudentsPageResults
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class FilteredStudentsPage(CohortAndGroupStudentPages,
                           FilteredStudentsPageFilters,
                           FilteredStudentsPageResults,
                           CuratedAddSelector,
                           CuratedModal):

    def search_and_create_new_student_cohort(self, cohort):
        self.click_sidebar_create_filtered()
        self.perform_student_search(cohort)
        self.create_new_cohort(cohort)

    EVERYONE_COHORT_LINK = By.XPATH, '//h1[text()="Everyone\'s Cohorts"]/../following-sibling::div//a'
    BACK_TO_COHORT_LINK = By.ID, 'back-to-cohort-link'

    @staticmethod
    def filtered_cohort_base_url(cohort_id):
        return f'{boa_utils.get_boa_base_url()}/cohort/{cohort_id}'

    def load_cohort(self, cohort):
        app.logger.info(f"Loading cohort id {cohort.cohort_id}, '{cohort.name}'")
        self.driver.get(self.filtered_cohort_base_url(cohort.cohort_id))
        self.wait_for_spinner()

    def load_and_delete_cohort(self, cohort):
        self.driver.get(self.filtered_cohort_base_url(cohort.cohort_id))
        self.delete_cohort(cohort)

    def hit_non_auth_cohort(self, cohort):
        self.driver.get(self.filtered_cohort_base_url(cohort.cohort_id))
        self.wait_for_404()

    def load_everyone_cohorts_page(self):
        self.driver.get(f'{boa_utils.get_boa_base_url()}/all/cohorts')
        self.wait_for_boa_title('Cohorts')

    def click_history(self):
        app.logger.info('Clicking History')
        self.wait_for_element_and_click(self.COHORT_HISTORY_LINK)
        Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_element_located(self.BACK_TO_COHORT_LINK))
