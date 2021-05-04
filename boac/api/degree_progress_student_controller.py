"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.api.degree_progress_api_utils import clone_degree_template
from boac.api.errors import BadRequestError, ResourceNotFoundError
from boac.api.util import can_edit_degree_progress, can_read_degree_progress, get_degree_checks_json
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param, is_int, to_int_or_none
from boac.models.degree_progress_category import DegreeProgressCategory
from boac.models.degree_progress_course import DegreeProgressCourse
from boac.models.degree_progress_note import DegreeProgressNote
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/degree/check/<sid>/create', methods=['POST'])
@can_edit_degree_progress
def create_degree_check(sid):
    params = request.get_json()
    template_id = get_param(params, 'templateId')
    if not template_id or not is_int(sid):
        raise BadRequestError('sid and templateId are required.')
    return tolerant_jsonify(clone_degree_template(template_id=template_id, sid=sid).to_api_json())


@app.route('/api/degree/course/copy', methods=['POST'])
@can_edit_degree_progress
def copy_course():
    params = request.get_json()
    category_id = to_int_or_none(get_param(params, 'categoryId'))
    section_id = to_int_or_none(get_param(params, 'sectionId'))
    sid = get_param(params, 'sid')
    term_id = to_int_or_none(get_param(params, 'termId'))
    if False in [is_int(v) for v in (category_id, section_id, sid, term_id)]:
        raise BadRequestError('category_id, section_id, sid, and term_id are required.')

    category = DegreeProgressCategory.find_by_id(category_id)
    courses = DegreeProgressCourse.get_courses(
        degree_check_id=category.template_id,
        section_id=section_id,
        sid=sid,
        term_id=term_id,
    )
    if not len(courses):
        raise ResourceNotFoundError('Course not found.')

    elif len(courses) == 1 and not courses[0].category_id:
        raise BadRequestError(f'Course {courses[0].id} is unassigned. Use the /assign API instead.')

    else:
        if not _can_accept_course_requirements(category):
            raise BadRequestError(f'A \'Course Requirement\' cannot be added to a {category.category_type}.')

        # Verify that course is not already in the requested category/subcategory.
        for c in DegreeProgressCourse.find_by_category_id(category.id):
            if c.section_id == section_id and c.sid == sid and c.term_id:
                raise BadRequestError(f'Course already belongs to category {category.name}.')
        for child in DegreeProgressCategory.find_by_parent_category_id(category_id):
            if child.id == category_id:
                raise BadRequestError(f'Course already belongs to category {category.name}.')

        # Create a new course instance and a new 'Course Requirement'.
        course = DegreeProgressCourse.create(
            degree_check_id=category.template_id,
            display_name=courses[0].display_name,
            grade=courses[0].grade,
            section_id=courses[0].section_id,
            sid=courses[0].sid,
            term_id=courses[0].term_id,
            units=courses[0].units,
        )
        course_requirement = DegreeProgressCategory.create(
            category_type='Course Requirement',
            name=courses[0].display_name,
            position=category.position,
            template_id=category.template_id,
            course_units=courses[0].units,
            parent_category_id=category.id,

        )
        DegreeProgressCourse.assign_category(category_id=course_requirement.id, course_id=course.id)
        return tolerant_jsonify(DegreeProgressCourse.find_by_id(course.id).to_api_json())


@app.route('/api/degree/course/<course_id>/assign', methods=['POST'])
@can_edit_degree_progress
def assign_course(course_id):
    params = request.get_json()
    course = DegreeProgressCourse.find_by_id(course_id)
    if course:
        category_id = get_param(params, 'categoryId')
        category = DegreeProgressCategory.find_by_id(category_id) if category_id else None
        if category:
            if category.template_id != course.degree_check_id:
                raise BadRequestError('The category and course do not belong to the same degree_check instance.')
            children = DegreeProgressCategory.find_by_parent_category_id(parent_category_id=category_id)
            if next((c for c in children if c.category_type == 'Subcategory'), None):
                raise BadRequestError('A course cannot be assigned to a category with a subcategory.')

        elif not category_id:
            # When user un-assigns a course we delete all copies of that course,.
            for copy_of_course in DegreeProgressCourse.get_courses(
                    degree_check_id=course.degree_check_id,
                    section_id=course.section_id,
                    sid=course.sid,
                    term_id=course.term_id,
            ):
                if copy_of_course.id != course.id:
                    # Due to on-cascade-delete in the db, this category deletion will cause deletion of the
                    # corresponding course, which is what we want. We are deleting copies of the course.
                    DegreeProgressCategory.delete(copy_of_course.category_id)

        course = DegreeProgressCourse.assign_category(category_id=category_id, course_id=course.id)
        return tolerant_jsonify(course.to_api_json())
    else:
        raise ResourceNotFoundError('Course not found.')


@app.route('/api/degrees/student/<sid>')
@can_read_degree_progress
def get_degree_checks(sid):
    return tolerant_jsonify(get_degree_checks_json(sid))


@app.route('/api/degree/course/<course_id>/update', methods=['POST'])
@can_edit_degree_progress
def update_course(course_id):
    params = request.get_json()
    note = get_param(params, 'note')
    # TODO: Add one-to-many unit_requirement mapping to db?
    # unit_requirements = get_param(params, 'unitRequirements')
    units = get_param(params, 'units')
    if units is None:
        raise BadRequestError('units parameter is required.')
    course = DegreeProgressCourse.update(course_id=course_id, note=note, units=units)
    return tolerant_jsonify(course.to_api_json())


@app.route('/api/degree/<degree_check_id>/note', methods=['POST'])
@can_edit_degree_progress
def update_degree_note(degree_check_id):
    params = request.get_json()
    body = get_param(params, 'body')
    note = DegreeProgressNote.upsert(
        body=body,
        template_id=degree_check_id,
        updated_by=current_user.get_id(),
    )
    return tolerant_jsonify(note.to_api_json())


def _can_accept_course_requirements(category):
    if category.category_type == 'Category':
        # Weird rule alert: A type='Category' can only have course requirements if it has no 'Subcategory'.
        return len(_get_category_children(category.id, 'Subcategory')) == 0
    else:
        return category.category_type == 'Subcategory'


def _get_category_children(category_id, category_type):
    children = DegreeProgressCategory.find_by_parent_category_id(category_id)
    return list(filter(lambda c: c.category_type == category_type, children))
