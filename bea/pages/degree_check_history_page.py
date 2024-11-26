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

from bea.pages.boa_pages import BoaPages
from selenium.webdriver.common.by import By


class DegreeCheckHistoryPage(BoaPages):

    CREATE_NEW_DEGREE_LINK = By.ID, 'create-new-degree'

    def visible_degree_names(self):
        return self.els_text_if_exist((By.XPATH, '//a[contains(@href, "/student/degree")]'))

    def visible_degree_update_dates(self):
        return self.els_text_if_exist((By.XPATH, '//td[@data-label="Last Updated"]/div'))

    def visible_degree_updated_by(self, degree):
        return self.el_text_if_exists((By.XPATH, f'//a[@id="degree-check-{degree.check_id}-link"]/ancestor::tr/td[3]//div'))

    @staticmethod
    def template_updated_alert_loc(degree):
        return By.XPATH, f'//tr[contains(., "{degree.name}")]/td[contains(., "Revisions to the original degree template")]'
