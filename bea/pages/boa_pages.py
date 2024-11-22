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
import datetime
import time

from bea.pages.create_note_modal import CreateNoteModal
from bea.pages.search_form import SearchForm
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class BoaPages(CreateNoteModal, SearchForm):

    SPINNER = (By.XPATH, '//*[@id="spinner-when-loading"]')
    MODAL = (By.CLASS_NAME, 'modal-content')
    NOT_FOUND = (By.XPATH, '//img[@alt="A silly boarding pass with the text, \'Error 404: Flight not found\'"]')
    ERROR_403 = (By.XPATH, '//div[text()=" HTTP error status: 403"]')

    ARE_YOU_SURE_CONFIRM_BUTTON = By.ID, 'are-you-sure-confirm'
    ARE_YOU_SURE_CANCEL_BUTTON = By.ID, 'are-you-sure-cancel'

    def wait_for_spinner(self):
        time.sleep(1)
        try:
            if self.is_present(BoaPages.SPINNER):
                self.when_not_visible(BoaPages.SPINNER, utils.get_short_timeout())
        except StaleElementReferenceException as e:
            app.logger.debug(f'{e}')

    def wait_for_boa_title(self, string):
        self.wait_for_title(f'{string} | BOA')

    def wait_for_403(self):
        self.when_present(self.ERROR_403, utils.get_short_timeout())

    def wait_for_404(self):
        Wait(self.driver, utils.get_short_timeout()).until(ec.visibility_of_element_located(self.NOT_FOUND))

    # HEADER

    HOME_LINK = (By.ID, 'home-header')
    HEADER_DROPDOWN = (By.ID, 'header-dropdown-under-name')
    DEGREE_CHECKS_LINK = (By.ID, 'header-menu-degree-check')
    FLIGHT_DATA_RECORDER_LINK = (By.ID, 'header-menu-analytics')
    FLIGHT_DECK_LINK = (By.ID, 'header-menu-flight-deck')
    PAX_MANIFEST_LINK = (By.ID, 'header-menu-passengers')
    PROFILE_LINK = (By.ID, 'header-menu-profile')
    FEEDBACK_LINK = (By.XPATH, '//a[contains(text(), "Feedback/Help")]')
    LOG_OUT_LINK = (By.ID, 'header-menu-log-out')
    STUDENT_NAME_HEADING = (By.ID, 'student-name-header')

    SERVICE_ALERT_BANNER = By.ID, 'service-announcement-banner'
    DISMISS_ALERT_BUTTON = By.ID, 'dismiss-service-announcement'

    def click_header_dropdown(self):
        self.wait_for_element_and_click(BoaPages.HEADER_DROPDOWN)

    def open_menu(self):
        if not self.is_present(BoaPages.LOG_OUT_LINK) or not self.element(BoaPages.LOG_OUT_LINK).is_displayed():
            app.logger.info('Clicking header menu button')
            self.click_header_dropdown()

    def click_degree_checks(self):
        app.logger.info('Clicking degree checks link in the header')
        if not self.is_present(BoaPages.HEADER_DROPDOWN):
            self.driver.get(f'{boa_utils.get_boa_base_url()}')
        self.open_menu()
        self.wait_for_page_and_click(self.DEGREE_CHECKS_LINK)

    def click_flight_deck_link(self):
        app.logger.info('Clicking flight deck link in the header')
        self.open_menu()
        self.wait_for_page_and_click(self.FLIGHT_DECK_LINK)

    def click_pax_manifest_link(self):
        app.logger.info('Clicking the pax manifest link in the header')
        self.open_menu()
        self.wait_for_page_and_click(self.PAX_MANIFEST_LINK)

    def click_profile_link(self):
        app.logger.info('Clicking profile link in the header')
        self.open_menu()
        self.wait_for_page_and_click(self.PROFILE_LINK)

    def log_out(self):
        app.logger.info('Logging out')
        if not self.is_present(BoaPages.HEADER_DROPDOWN):
            self.driver.get(f'{boa_utils.get_boa_base_url()}')
        self.open_menu()
        self.wait_for_element_and_click(BoaPages.LOG_OUT_LINK)

        # In case logout doesn't work the first time, try again
        time.sleep(2)
        if self.is_present(BoaPages.LOG_OUT_LINK):
            if not self.element(BoaPages.LOG_OUT_LINK).is_displayed():
                self.open_menu()
                self.wait_for_element_and_click(BoaPages.LOG_OUT_LINK)
            time.sleep(2)

        self.wait_for_boa_title('Welcome')

    def visible_service_alert(self):
        return self.el_text_if_exists(self.SERVICE_ALERT_BANNER)

    def dismiss_service_alert(self):
        self.wait_for_element_and_click(self.DISMISS_ALERT_BUTTON)
        self.when_not_visible(self.SERVICE_ALERT_BANNER, 1)

    # SIDEBAR - FILTERED COHORTS

    CREATE_FILTERED_COHORT_LINK = (By.ID, 'cohort-create')
    VIEW_EVERYONE_COHORTS_LINK = (By.ID, 'cohorts-all')
    FILTERED_COHORT_LINK = (By.XPATH, '//a[contains(@id,"sidebar-cohort")]')
    DUPE_FILTERED_NAME_MSG = (
        By.XPATH,
        '//div[contains(text(), "You have an existing cohort with this name. Please choose a different name.")]')

    def click_sidebar_create_filtered(self):
        app.logger.info('Clicking sidebar button to create a filtered cohort')
        self.wait_for_page_and_click(self.CREATE_FILTERED_COHORT_LINK)
        self.wait_for_boa_title('Create Cohort')
        time.sleep(utils.get_click_sleep())

    def click_view_everyone_cohorts(self):
        time.sleep(1)
        self.wait_for_page_and_click(self.VIEW_EVERYONE_COHORTS_LINK)
        self.wait_for_boa_title('All Cohorts')

    def click_sidebar_filtered_link(self, cohort):
        links = self.elements(self.FILTERED_COHORT_LINK)
        link = next(filter(lambda el: el.text == cohort.name, links))
        link.click()

    @staticmethod
    def sidebar_member_count_loc(cohort):
        return By.XPATH, f'//a[contains(@id,"sidebar-")][contains(.,"{cohort.name}")]/span[contains(@id, "count")]'

    def wait_for_sidebar_member_count(self, cohort):
        app.logger.info(f'Waiting for cohort {cohort.name} member count of {len(cohort.members)}')
        tries = utils.get_short_timeout()
        while tries > 0:
            try:
                tries -= 1
                self.when_present(self.sidebar_member_count_loc(cohort), utils.get_short_timeout())
                utils.assert_equivalence(self.element(self.sidebar_member_count_loc(cohort)).text.split()[0],
                                         f'{len(cohort.members)}')
                break
            except (AssertionError, TimeoutError):
                if tries == 0:
                    raise
                else:
                    time.sleep(1)

    # SIDEBAR - CURATED GROUPS

    CREATE_CURATED_GROUP_LINK = By.ID, 'create-curated-group-from-sidebar'
    VIEW_EVERYONE_GROUPS_LINK = By.ID, 'groups-all'
    SIDEBAR_GROUP_LINK = By.XPATH, '//a[contains(@id, "sidebar-curated-group")]'
    SIDEBAR_GROUP_NAME = By.XPATH, '//a[contains(@id, "sidebar-curated-group")]/div'

    CREATE_ADMIT_GROUP_LINK = By.ID, 'create-admissions-group-from-sidebar'
    SIDEBAR_ADMIT_GROUP_LINK = By.XPATH, '//a[contains(@id, "sidebar-admissions-group")]'

    def click_sidebar_create_student_group(self):
        app.logger.info('Clicking sidebar button to create a curated group')
        self.wait_for_page_and_click(self.CREATE_CURATED_GROUP_LINK)
        time.sleep(1)

    def click_sidebar_create_admit_group(self):
        app.logger.info('Clicking sidebar button to create an admit group')
        self.wait_for_page_and_click(self.CREATE_ADMIT_GROUP_LINK)
        time.sleep(1)

    def sidebar_student_groups(self):
        time.sleep(utils.get_click_sleep())
        return list(map(lambda a: a.text, self.elements(self.SIDEBAR_GROUP_NAME)))

    def sidebar_admit_groups(self):
        time.sleep(utils.get_click_sleep())
        return list(map(lambda a: a.text, self.elements(self.SIDEBAR_ADMIT_GROUP_LINK)))

    def click_view_everyone_groups(self):
        time.sleep(1)
        self.wait_for_page_and_click(self.VIEW_EVERYONE_GROUPS_LINK)
        self.wait_for_boa_title('All Groups')

    def click_sidebar_group_link(self, group):
        els = self.elements(self.SIDEBAR_ADMIT_GROUP_LINK) if group.is_ce3 else self.elements(self.SIDEBAR_GROUP_LINK)
        link = next(filter(lambda a: a.text == group.name, els))
        link.click()

    def wait_for_sidebar_group(self, group):
        self.wait_for_sidebar_member_count(group)
        if not group.cohort_id:
            boa_utils.set_curated_group_id(group)
        if group.is_ce3:
            assert group.name in self.sidebar_admit_groups()
        else:
            assert group.name in self.sidebar_student_groups()

    # SIDEBAR - CE3 COHORTS

    CREATE_CE3_FILTERED_LINK = By.ID, 'admitted-students-cohort-create'
    ALL_ADMITS_LINK = By.ID, 'admitted-students-all'

    def click_sidebar_all_admits(self):
        app.logger.info('Clicking sidebar link to view all CE3 admits')
        self.wait_for_page_and_click(self.ALL_ADMITS_LINK)
        self.wait_for_spinner()
        self.when_present((By.XPATH, '//h1[contains(text(), "CE3 Admissions")]'), utils.get_short_timeout())

    def click_sidebar_create_ce3_filtered(self):
        app.logger.info('Clicking sidebar button to create a CE3 cohort')
        self.wait_for_page_and_click(self.CREATE_CE3_FILTERED_LINK)
        self.when_present((By.XPATH, '//h1[text()=" Create an admissions cohort"]'), utils.get_short_timeout())
        time.sleep(1)

    # SIDEBAR - DRAFT NOTES

    DRAFT_NOTES_LINK = By.ID, 'link-to-draft-notes'

    def draft_note_count(self):
        return self.el_text_if_exists((By.ID, 'draft-note-count'))

    def click_draft_notes(self):
        app.logger.info('Clicking link to Draft Notes page')
        self.wait_for_element_and_click(self.DRAFT_NOTES_LINK)

    def wait_for_draft_note(self, note, manual_update=False):
        self.hit_tab()
        time.sleep(2)
        tries = 0
        max_tries = 1 if manual_update else 3
        while tries <= max_tries:
            tries += 1
            try:
                results = boa_utils.get_note_ids_by_subject(note)
                assert results
                note.record_id = results[0]
                note.created_date = datetime.datetime.now()
                note.updated_date = datetime.datetime.now()
                break
            except AssertionError:
                if tries == max_tries:
                    raise
                else:
                    time.sleep(5)

    @staticmethod
    def wait_for_draft_note_update(note, manual_update=False):
        expected_subj = note.subject or ''
        expected_create_date = note.created_date and note.created_date.strftime('%Y-%m-%d')
        expected_set_date = note.set_date and note.set_date.strftime('%Y-%m-%d')
        expected_attachments = [a.file_name for a in note.attachments]
        expected_attachments.sort()
        expected_topics = [t.name for t in note.topics]
        expected_topics.sort()
        tries = 0
        max_tries = 2 if manual_update else 8
        while tries <= max_tries:
            try:
                tries += 1
                time.sleep(3)
                saved_note = boa_utils.get_notes_by_ids([note.record_id])[0]
                actual_create_date = saved_note.created_date and saved_note.created_date.strftime('%Y-%m-%d')
                actual_set_date = saved_note.set_date and saved_note.set_date.strftime('%Y-%m-%d')
                actual_attachments = [a.file_name for a in saved_note.attachments]
                actual_attachments.sort()
                actual_topics = [t for t in saved_note.topics]
                actual_topics.sort()
                utils.assert_equivalence(saved_note.subject, expected_subj)
                utils.assert_equivalence(saved_note.body, note.body)
                utils.assert_equivalence(saved_note.advisor.uid, note.advisor.uid)
                utils.assert_equivalence(saved_note.is_draft, note.is_draft)
                utils.assert_equivalence(saved_note.is_private, note.is_private)
                utils.assert_equivalence(actual_create_date, expected_create_date)
                utils.assert_equivalence(actual_set_date, expected_set_date)
                utils.assert_equivalence(actual_attachments, expected_attachments)
                utils.assert_equivalence(actual_topics, expected_topics)
            except AssertionError:
                if tries == max_tries:
                    raise

    @staticmethod
    def expected_draft_note_subject(note):
        return note.subject.strip() if note.subject else '[DRAFT NOTE]'

    # BOX_PLOTS

    @staticmethod
    def boxplot_xpath():
        return '//*[name()="svg"]/*[name()="g"][@class="highcharts-series-group"]'

    def boxplot_trigger_xpath(self):
        return f'{self.boxplot_xpath()}/*[name()="g"]/*[name()="g"]/*[name()="path"][3]'

    @staticmethod
    def verify_list_view_sorting(visible_sids, expected_sids):
        # Only compare sort order for SIDs that are both expected and visible
        if not sorted(expected_sids) == sorted(visible_sids):
            expected_sids = [s for s in expected_sids if s in visible_sids]
            visible_sids = [s for s in visible_sids if s in expected_sids]
        sorting_errors = []
        for v in visible_sids:
            e = expected_sids[visible_sids.index(v)]
            if not v == e:
                sorting_errors.append(f'Expected {e}, got {v}')
        app.logger.info(f'Mismatches: {sorting_errors}')
        assert not sorting_errors
