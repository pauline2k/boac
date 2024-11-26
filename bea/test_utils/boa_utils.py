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
from datetime import datetime
from itertools import groupby
import re

from bea.models.advisor_role import AdvisorRole
from bea.models.alert import Alert
from bea.models.cohorts_and_groups.cohort import Cohort
from bea.models.cohorts_and_groups.filtered_cohort import FilteredCohort
from bea.models.degree_progress.degree_check_perms import DegreeCheckPerms
from bea.models.department import Department
from bea.models.department_membership import DepartmentMembership
from bea.models.notes_and_appts.note import Note
from bea.models.notes_and_appts.note_attachment import NoteAttachment
from bea.models.notes_and_appts.note_template import NoteTemplate
from bea.models.notes_and_appts.timeline_record_source import TimelineRecordSource
from bea.models.student import Student
from bea.models.user import User
from bea.test_utils import utils
from boac import db, std_commit
from flask import current_app as app
from sqlalchemy import text


def get_boa_base_url():
    return app.config['BASE_URL']


def unique_students_in_batch(students, cohorts, groups):
    uniques = []
    uniques.extend(students)
    for cohort in cohorts:
        for c_member in cohort.members:
            if c_member not in uniques:
                uniques.append(c_member)
    for group in groups:
        for g_member in group.members:
            if g_member not in uniques:
                uniques.append(g_member)
    return uniques


# USERS

def get_user_login_count(user):
    sql = f"SELECT COUNT(uid) FROM user_logins WHERE uid = '{user.uid}'"
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    return result['count']


def create_admin_user(user):
    sql = f"""INSERT INTO authorized_users (created_at, updated_at, uid, is_admin, in_demo_mode,
                                            can_access_canvas_data, created_by, is_blocked)
              SELECT now(), now(), '{user.uid}', true, false, true, '{utils.get_admin_uid()}', false
               WHERE NOT EXISTS (SELECT id FROM authorized_users WHERE uid = '{user.uid}')"""
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)


def soft_delete_user(user):
    sql = f"UPDATE authorized_users SET deleted_at = NOW() WHERE uid = '{user.uid}'"
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)


def hard_delete_user(user):
    sql_1 = f"DELETE FROM authorized_users WHERE uid = '{user.uid}'"
    app.logger.info(sql_1)
    db.session.execute(text(sql_1))
    std_commit(allow_test_environment=True)
    sql_2 = f"DELETE FROM json_cache WHERE key = 'calnet_user_for_uid_' || '{user.uid}'"
    app.logger.info(sql_2)
    db.session.execute(text(sql_2))
    std_commit(allow_test_environment=True)


def restore_user(user):
    sql = f"UPDATE authorized_users SET deleted_at = NULL WHERE uid = '{user.uid}'"
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)


def get_authorized_users():
    auth_users = []
    sql = """SELECT authorized_users.uid AS uid,
                    authorized_users.can_access_advising_data AS can_access_advising_data,
                    authorized_users.can_access_canvas_data AS can_access_canvas_data,
                    authorized_users.deleted_at AS deleted_at,
                    authorized_users.is_admin AS is_admin,
                    authorized_users.is_blocked AS is_blocked,
                    authorized_users.degree_progress_permission AS deg_prog_perm,
                    authorized_users.automate_degree_progress_permission AS deg_prog_automated,
                    university_dept_members.automate_membership AS is_automated,
                    university_dept_members.role AS advisor_role,
                    university_depts.dept_code AS dept_code
               FROM authorized_users
          LEFT JOIN university_dept_members
                 ON authorized_users.id = university_dept_members.authorized_user_id
          LEFT JOIN university_depts
                 ON university_dept_members.university_dept_id = university_depts.id
           ORDER BY uid ASC;"""
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)

    advisors = groupby(results, key=lambda u: u.uid)
    for k, v in advisors:
        app.logger.info(f'Getting advisor role(s) for UID {k}')
        v = list(v)
        active = False if v[0]['deleted_at'] else True
        can_access_advising_data = v[0]['can_access_advising_data']
        can_access_canvas_data = v[0]['can_access_canvas_data']
        is_admin = v[0]['is_admin']
        is_blocked = v[0]['is_blocked']
        degree_progress_automated = v[0]['deg_prog_automated']
        if v[0]['deg_prog_perm'] == 'read':
            degree_progress_perm = DegreeCheckPerms.READ
        elif v[0]['deg_prog_perm'] == 'read_write':
            degree_progress_perm = DegreeCheckPerms.WRITE
        else:
            degree_progress_perm = None

        memberships = []
        for dept_memb in v:
            role = dept_memb['advisor_role'] and next(filter(lambda r: (r.value['code'] == dept_memb['advisor_role']), AdvisorRole))
            dept = dept_memb['dept_code'] and next(filter(lambda d: (d.value['code'] == dept_memb['dept_code']), Department))
            is_automated = dept_memb['is_automated']
            membership = DepartmentMembership(advisor_role=role,
                                              dept=dept,
                                              is_automated=is_automated)
            memberships.append(membership)

        user = User({
            'uid': str(k),
            'active': active,
            'can_access_advising_data': can_access_advising_data,
            'can_access_canvas_data': can_access_canvas_data,
            'degree_progress_perm': degree_progress_perm,
            'degree_progress_automated': degree_progress_automated,
            'dept_memberships': memberships,
            'depts': [m.dept for m in memberships],
            'is_admin': is_admin,
            'is_blocked': is_blocked,
        })
        auth_users.append(user)

    app.logger.info(f'There are {len(auth_users)} authorized users')
    return auth_users


def get_dept_advisors(dept, membership=None):
    clause = ''
    # "Notes Only" isn't a real department, so it's a special case
    if dept == Department.NOTES_ONLY:
        if membership:
            role_code = membership.advisor_role.value['code']
            clause = f"AND university_dept_members.role = '{role_code}'"
        sql = f"""SELECT authorized_users.uid AS uid,
                         authorized_users.can_access_advising_data AS can_access_advising_data,
                         authorized_users.can_access_canvas_data AS can_access_canvas_data,
                         authorized_users.degree_progress_permission AS deg_prog_perm,
                         string_agg(ud.dept_code,',') AS depts
                    FROM authorized_users
                    JOIN university_dept_members
                      ON authorized_users.id = university_dept_members.authorized_user_id
                    JOIN university_depts ud
                      ON university_dept_members.university_dept_id = ud.id
                   WHERE authorized_users.deleted_at IS NULL
                     AND authorized_users.can_access_canvas_data IS FALSE
                        {clause}
                GROUP BY authorized_users.uid,
                         authorized_users.can_access_advising_data,
                         authorized_users.can_access_canvas_data,
                         authorized_users.degree_progress_permission"""
    else:
        if membership:
            role_code = membership.advisor_role.value['code']
            clause = f"AND udm1.role = '{role_code}'"
        sql = f"""SELECT authorized_users.uid AS uid,
                         authorized_users.can_access_advising_data AS can_access_advising_data,
                         authorized_users.can_access_canvas_data AS can_access_canvas_data,
                         authorized_users.degree_progress_permission AS deg_prog_perm,
                         string_agg(ud2.dept_code,',') AS depts
                    FROM authorized_users
                    JOIN university_dept_members udm1
                      ON authorized_users.id = udm1.authorized_user_id
                    JOIN university_depts ud1
                      ON udm1.university_dept_id = ud1.id
                     AND ud1.dept_code = '{dept.value['code']}'
                    JOIN university_dept_members udm2
                      ON authorized_users.id = udm2.authorized_user_id
                    JOIN university_depts ud2
                      ON udm2.university_dept_id = ud2.id
                   WHERE authorized_users.deleted_at IS NULL
                        {clause}
                GROUP BY authorized_users.uid,
                         authorized_users.can_access_advising_data,
                         authorized_users.can_access_canvas_data,
                         authorized_users.degree_progress_permission"""

    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    advisors = []
    for row in result:

        depts = []
        dept_memberships = []
        dept_codes = row['depts'].split(',')
        for dc in dept_codes:
            for dept in Department:
                if dept.value['code'] == dc:
                    depts.append(dept)
                    dept_memberships.append(dept)

        if row['deg_prog_perm'] == 'read':
            degree_progress_perm = DegreeCheckPerms.READ
        elif row['deg_prog_perm'] == 'read_write':
            degree_progress_perm = DegreeCheckPerms.WRITE
        else:
            degree_progress_perm = None

        user = User({
            'uid': str(row['uid']),
            'active': True,
            'can_access_advising_data': row['can_access_advising_data'],
            'can_access_canvas_data': row['can_access_canvas_data'],
            'degree_progress_perm': degree_progress_perm,
            'depts': depts,
            'dept_memberships': dept_memberships,
        })
        advisors.append(user)
    return advisors


def get_advisor_names(advisor):
    sql = f"""SELECT author_name,
                     created_at
                FROM notes
               WHERE author_uid = '{advisor.uid}'
            ORDER BY created_at DESC"""
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)

    names = list(map(lambda n: n['author_name'], result))
    names = list(set(names))
    if names:
        advisor.full_name = names[0]
        advisor.alt_names = names[1::]


def get_director(auth_users):
    directors = []
    for u in auth_users:
        for m in u.dept_memberships:
            if m.advisor_role and m.advisor_role.value['code'] == AdvisorRole.DIRECTOR.value['code']:
                directors.append(u)
    return directors[0]


def get_advising_data_advisor(dept, test_advisor):
    dept_advisors = get_dept_advisors(dept)
    dept_advisors.reverse()
    app.logger.info(f'Dept advisor UIDs are {list(map(lambda a: a.uid, dept_advisors))}')
    for a in dept_advisors:
        if a.can_access_advising_data and a.uid != test_advisor.uid:
            return a


def get_user_filtered_cohorts(user, admits=False):
    cohorts = []
    domain = 'admitted_students' if admits else 'default'
    sql = f"""SELECT cohort_filters.id AS cohort_id,
                     cohort_filters.name AS cohort_name,
                     cohort_filters.filter_criteria AS criteria
                FROM cohort_filters
                JOIN authorized_users ON authorized_users.id = cohort_filters.owner_id
               WHERE cohort_filters.domain = '{domain}'
                 AND authorized_users.uid = '{user.uid}'"""
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    for row in results:
        cohort = FilteredCohort({
            'cohort_id': row['cohort_id'],
            'is_ce3': admits,
            'name': row['cohort_name'],
            'owner_uid': user.uid,
        })
        cohorts.append(cohort)
    return cohorts


def get_user_curated_groups(user, admits=False):
    groups = []
    domain = 'admitted_students' if admits else 'default'
    sql = f"""SELECT student_groups.id AS cohort_id,
                     student_groups.name AS group_name
                FROM student_groups
                JOIN authorized_users ON authorized_users.id = student_groups.owner_id
               WHERE student_groups.domain = '{domain}'
                 AND authorized_users.uid = '{user.uid}'"""
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    for row in results:
        group = Cohort({
            'cohort_id': row['cohort_id'],
            'is_ce3': admits,
            'name': row['group_name'],
            'owner_uid': user.uid,
        })
        groups.append(group)
    return groups


def get_everyone_filtered_cohorts(dept=None, admits=False):
    cohorts = []
    if dept:
        dept_clause = f""" JOIN university_dept_members
                             ON university_dept_members.authorized_user_id = authorized_users.id
                           JOIN university_depts
                             ON university_depts.id = university_dept_members.university_dept_id
                          WHERE university_depts.dept_code = '{dept.value['code']}'"""
    else:
        dept_clause = ''
    conjunction = 'AND' if dept else 'WHERE'
    domain = 'admitted_students' if admits else 'default'

    sql = f"""SELECT cohort_filters.id AS cohort_id,
                     cohort_filters.name AS cohort_name,
                     cohort_filters.filter_criteria AS criteria,
                     authorized_users.uid AS uid
                FROM cohort_filters
                JOIN authorized_users
                  ON authorized_users.id = cohort_filters.owner_id
                 AND authorized_users.deleted_at IS NULL
                {dept_clause} {conjunction} cohort_filters.domain = '{domain}'
            ORDER BY uid, cohort_id ASC"""
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    for row in results:
        cohort = FilteredCohort({
            'cohort_id': row['cohort_id'],
            'is_ce3': admits,
            'name': re.sub(r'\s+', ' ', row['cohort_name']).strip(),
            'owner_uid': row['uid'],
        })
        cohorts.append(cohort)
    cohorts.sort(key=lambda c: [int(c.owner_uid), c.name])
    return cohorts


def get_everyone_curated_groups(dept=None, admits=False):
    groups = []
    if dept:
        dept_clause = f""" JOIN university_dept_members
                             ON university_dept_members.authorized_user_id = authorized_users.id
                           JOIN university_depts
                             ON university_depts.id = university_dept_members.university_dept_id
                          WHERE university_depts.dept_code = '{dept.value['code']}'"""
    else:
        dept_clause = ''
    conjunction = 'AND' if dept else 'WHERE'
    domain = 'admitted_students' if admits else 'default'

    sql = f"""SELECT student_groups.id AS group_id,
                     student_groups.name AS group_name,
                     authorized_users.uid AS uid
                FROM student_groups
                JOIN authorized_users
                  ON authorized_users.id = student_groups.owner_id
                 AND authorized_users.deleted_at IS NULL
                {dept_clause} {conjunction} student_groups.domain = '{domain}'
            ORDER BY uid, group_id ASC"""
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    for row in results:
        group = Cohort({
            'cohort_id': row['group_id'],
            'is_ce3': admits,
            'name': re.sub(r'\s+', ' ', row['group_name']).strip(),
            'owner_uid': row['uid'],
        })
        groups.append(group)
    groups.sort(key=lambda c: [int(c.owner_uid), c.name])
    return groups


# NOTES


def get_sids_with_notes_of_src_boa(drafts=False):
    sql = f"""SELECT DISTINCT sid
                FROM notes
               WHERE body NOT LIKE '%QA Test%'
                 AND deleted_at IS NULL
                 AND is_private IS FALSE
                 AND is_draft IS {'TRUE' if drafts else 'FALSE'}"""
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    return list(map(lambda r: r['sid'], results))


def get_note_ids_by_subject(note, student=None):
    if student:
        clause = f" AND sid = '{student.sid}'"
    else:
        clause = ''
    sql = f"""SELECT id
                FROM notes
               WHERE subject = '{note.subject}'{clause}
                 AND deleted_at IS NULL;
    """
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    return list(map(lambda r: str(r['id']), results))


def get_note_sids_by_subject(note):
    sql = f"""SELECT sid
                FROM notes
               WHERE subject = '{note.subject}'
                 AND deleted_at IS NULL"""
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    return list(map(lambda r: str(r['sid']), results))


def get_student_notes(student):
    sql = f"SELECT * FROM notes WHERE sid = '{student.sid}'"
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    return get_notes_from_pg_db_result(results, student)


def get_notes_by_ids(ids):
    sql = f'SELECT * FROM notes WHERE id IN ({utils.in_op(ids)})'
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    return get_notes_from_pg_db_result(results)


def get_advisor_note_drafts(advisor=None):
    adv_clause = f" AND author_uid = '{advisor.uid}'" if advisor else ''
    sql = f"""SELECT *
                FROM notes
               WHERE is_draft IS TRUE
                 AND deleted_at IS NULL{adv_clause}"""
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    return get_notes_from_pg_db_result(results)


def get_notes_from_pg_db_result(results, student=None):
    notes = []
    for row in results:
        app.logger.info(f"Gathering data for BOA note ID {row['id']}")

        depts = list(filter(lambda d: d.value['code'] in row['author_dept_codes'], Department))
        advisor = User({
            'depts': list(map(lambda d: d.value['name'], depts)),
            'full_name': row['author_name'],
            'role': row['author_role'],
            'uid': row['author_uid'],
        })
        student = student or row['sid'] and Student({'sid': row['sid']})
        if row['set_date']:
            set_date_str = row['set_date'].strftime('%Y-%m-%d')
            set_date = datetime.strptime(set_date_str, '%Y-%m-%d')
        else:
            set_date = row['set_date']
        note_data = {
            'advisor': advisor,
            'body': (utils.strip_tags_and_whitespace(row['body']) if row['body'] else None),
            'created_date': (row['created_at'] and utils.date_to_local_tz(row['created_at'])),
            'deleted_date': (row['deleted_at'] and utils.date_to_local_tz(row['deleted_at'])),
            'is_draft': row['is_draft'],
            'is_private': row['is_private'],
            'record_id': str(row['id']),
            'set_date': (set_date and utils.date_to_local_tz(set_date)),
            'source': TimelineRecordSource.BOA,
            'student': student,
            'subject': utils.strip_tags_and_whitespace(row['subject']),
            'updated_date': (row['updated_at'] and utils.date_to_local_tz(row['updated_at'])),
        }

        attachments = []
        attach_query = f"SELECT * FROM note_attachments WHERE note_id = '{row['id']}' AND deleted_at IS NULL"
        app.logger.info(attach_query)
        attach_results = db.session.execute(text(attach_query))
        std_commit(allow_test_environment=True)
        for a in attach_results:
            if a['note_id'] == row['id']:
                file_name = a['path_to_attachment'].split('/')[-1]
                if not re.sub(r'(20)\d{6}(_)\d{6}(_)', '', file_name[0:16]):
                    visible_file_name = file_name[16:]
                else:
                    visible_file_name = file_name
                attachments.append(NoteAttachment({
                    'attachment_id': a['id'],
                    'file_name': visible_file_name.lower(),
                    'deleted_at': a['deleted_at'],
                }))

        topics = []
        topic_query = f"SELECT note_id, topic FROM note_topics WHERE note_id = '{row['id']}' AND deleted_at IS NULL"
        app.logger.info(topic_query)
        topic_results = db.session.execute(text(topic_query))
        std_commit(allow_test_environment=True)
        for t in topic_results:
            if t['note_id'] == row['id']:
                topics.append(t['topic'])

        notes.append(Note(attachments=attachments,
                          data=note_data,
                          topics=topics))
    return notes


def is_note_private(note):
    sql = f"SELECT is_private FROM notes WHERE id = '{note.record_id}'"
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    return [row['is_private'] for row in result][0]


def get_attachment_id_by_file_name(note, attachment):
    sql = f"""SELECT id
                FROM note_attachments
               WHERE note_id = {note.record_id}
                 AND path_to_attachment LIKE '%{attachment.file_name}'"""
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    ids = [row['id'] for row in result]
    attachment.attachment_id = ids[-1]


def get_topic_id(topic):
    sql = f"""SELECT id
                FROM topics
               WHERE topic = '{topic.name}'"""
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    topic.topic_id = [row['id'] for row in result][0]
    return topic.topic_id


def get_user_note_templates(user):
    sql = f"""SELECT note_templates.id
                FROM note_templates
               JOIN authorized_users ON note_templates.creator_id = authorized_users.id
              WHERE authorized_users.uid = '{user.uid}'
                AND note_templates.deleted_at IS NULL"""
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    templates = []
    for row in results:
        templates.append(NoteTemplate({'record_id': row['id']}))
    return templates


def get_note_template_ids(template):
    sql = f"SELECT id FROM note_templates WHERE title = '{template.title}'"
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    return list(map(lambda r: str(r['id']), results))


def hard_delete_template(template_id):
    sql = f"DELETE FROM note_templates WHERE id = '{template_id}'"
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)


def generate_note_search_query(note):
    search_string = ''
    if note.subject:
        string = note.subject
    elif note.body and 'http' not in note.body:
        string = note.body
    else:
        string = None
    if string:
        phrases = re.split(r'(<\w+>|<\/\w+>)', string)
        for phrase in phrases:
            if len(phrase) > 24:
                phrase = phrase.split(' ')[:4]
                search_string = ' '.join(phrase).strip()
    return search_string


def generate_appt_search_query(appt):
    search_string = ''
    if appt.detail:
        phrases = re.split(r'(<\w+>|<\/\w+>)', appt.detail)
        for phrase in phrases:
            if len(phrase) > 24:
                phrase = phrase.split(' ')[:4]
                search_string = ' '.join(phrase).strip()
    return search_string


# COHORTS

def set_filtered_cohort_id(cohort):
    sql = f"""SELECT id
                FROM cohort_filters
               WHERE name = '{cohort.name}'"""
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    cohort_id = [row['id'] for row in result][0]
    app.logger.info(f'Filtered cohort {cohort.name} ID is {cohort_id}')
    cohort.cohort_id = cohort_id


# GROUPS

def append_new_members_to_group(group, members):
    for m in members:
        if m not in group.members:
            group.members.append(m)


def set_curated_group_id(group):
    sql = f"""SELECT id
                FROM student_groups
               WHERE name = '{group.name}'"""
    app.logger.info(sql)
    result = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    group_id = [row['id'] for row in result][0]
    app.logger.info(f'Curated group {group.name} ID is {group_id}')
    group.cohort_id = group_id


# ALERTS

def get_students_alerts(users):
    sids = utils.in_op(list(map(lambda u: u.sid, users)))
    sql = f"""SELECT id,
                     sid,
                     alert_type,
                     message,
                     created_at,
                     updated_at
                FROM alerts
               WHERE sid IN ({sids})
                 AND deleted_at IS NULL
                 AND key LIKE '{utils.get_current_term().sis_id}%'
                 AND alert_type != 'hold'"""
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    alerts = []
    for r in results:
        if r['alert_type'] in ['midterm', 'withdrawal']:
            date = r['created_at']
        else:
            date = r['updated_at']
        student = Student({
            'sid': r['sid'],
        })
        alert = Alert({
            'alert_id': r['id'],
            'date': date,
            'message': re.sub(r'\s+', ' ', r['message']),
            'student': student,
            'alert_type': r['alert_type'],
        })
        alerts.append(alert)
    alerts.sort(key=lambda a: a.message)
    return alerts


def get_un_dismissed_users_alerts(students, advisor=None):
    alerts = get_students_alerts(students)
    dismissed = get_dismissed_alerts(alerts, advisor)
    return list(set(alerts) - set(dismissed))


def get_dismissed_alerts(alerts, advisor=None):
    if alerts:
        alert_ids = utils.in_op(list(map(lambda a: a.alert_id, alerts)))
        uid = advisor.uid if advisor else utils.get_admin_uid()
        sql = f"""SELECT alert_views.alert_id
                    FROM alert_views
                    JOIN authorized_users ON authorized_users.id = alert_views.viewer_id
                   WHERE alert_views.alert_id IN ({alert_ids})
                     AND authorized_users.uid = '{uid}'"""
        app.logger.info(sql)
        results = db.session.execute(text(sql))
        std_commit(allow_test_environment=True)
        dismissed = []
        for r in results:
            dismissed.append(str(r['alert_id']))
        return list(filter(lambda a: a.alert_id in dismissed, alerts))
    else:
        return []


def get_members_with_alerts(cohort, cohort_member_alerts):
    alert_members = []
    for member in cohort.members:
        member.alert_count = len(list(filter(lambda a: a.student.sid == member.sid, cohort_member_alerts)))
        if member.alert_count != 0:
            alert_members.append(member)
    return alert_members
