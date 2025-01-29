/**
 * Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--

CREATE TABLE alert_views (
    alert_id integer NOT NULL,
    viewer_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    dismissed_at timestamp with time zone
);
ALTER TABLE alert_views OWNER TO boac;
ALTER TABLE ONLY alert_views
    ADD CONSTRAINT alert_views_pkey PRIMARY KEY (alert_id, viewer_id);
CREATE INDEX alert_views_dismissed_at_idx ON alert_views (dismissed_at);
CREATE INDEX alert_views_viewer_id_idx ON alert_views USING btree (viewer_id);

--

CREATE TABLE alerts (
    id integer NOT NULL,
    sid character varying(80) NOT NULL,
    alert_type character varying(80) NOT NULL,
    key character varying(255) NOT NULL,
    message text NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
ALTER TABLE alerts OWNER TO boac;
CREATE SEQUENCE alerts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE alerts_id_seq OWNER TO boac;
ALTER SEQUENCE alerts_id_seq OWNED BY alerts.id;
ALTER TABLE ONLY alerts ALTER COLUMN id SET DEFAULT nextval('alerts_id_seq'::regclass);
ALTER TABLE ONLY alerts
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (id);
ALTER TABLE ONLY alerts
    ADD CONSTRAINT alerts_sid_alert_type_key_created_at_unique_constraint UNIQUE (sid, alert_type, key, created_at);
CREATE INDEX alerts_deleted_at_idx ON alerts (deleted_at);
CREATE INDEX alerts_sid_idx ON alerts USING btree (sid);

--

CREATE TABLE appointments_read (
    appointment_id VARCHAR(255) NOT NULL,
    viewer_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE appointments_read OWNER TO boac;
ALTER TABLE ONLY appointments_read
    ADD CONSTRAINT appointments_read_pkey PRIMARY KEY (viewer_id, appointment_id);
CREATE INDEX appointments_read_appointment_id_idx ON appointments_read USING btree (appointment_id);
CREATE INDEX appointments_read_viewer_id_idx ON appointments_read USING btree (viewer_id);

--

CREATE TYPE generic_permission_types AS ENUM ('read', 'read_write');

--

CREATE TABLE authorized_users (
    automate_degree_progress_permission BOOLEAN DEFAULT FALSE NOT NULL,
    can_access_advising_data boolean DEFAULT true NOT NULL,
    can_access_canvas_data boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone NOT NULL,
    created_by character varying(255) NOT NULL,
    degree_progress_permission generic_permission_types,
    deleted_at timestamp with time zone,
    id integer NOT NULL,
    in_demo_mode boolean DEFAULT false NOT NULL,
    is_admin boolean,
    is_blocked boolean DEFAULT false NOT NULL,
    is_peer_advisor boolean DEFAULT false NOT NULL,
    search_history CHARACTER VARYING[],
    uid character varying(255) NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
ALTER TABLE authorized_users OWNER TO boac;
CREATE SEQUENCE authorized_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE authorized_users_id_seq OWNER TO boac;
ALTER SEQUENCE authorized_users_id_seq OWNED BY authorized_users.id;
ALTER TABLE ONLY authorized_users ALTER COLUMN id SET DEFAULT nextval('authorized_users_id_seq'::regclass);
ALTER TABLE ONLY authorized_users
    ADD CONSTRAINT authorized_users_pkey PRIMARY KEY (id);
ALTER TABLE ONLY authorized_users
    ADD CONSTRAINT authorized_users_uid_key UNIQUE (uid);

--

CREATE TYPE cohort_filter_event_types AS ENUM ('added', 'removed');

--

CREATE TABLE cohort_filter_events (
    id integer NOT NULL,
    cohort_filter_id integer NOT NULL,
    sid character varying(80) NOT NULL,
    event_type cohort_filter_event_types NOT NULL,
    created_at timestamp with time zone NOT NULL
);
ALTER TABLE cohort_filter_events OWNER TO boac;
CREATE SEQUENCE cohort_filter_events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE cohort_filter_events_id_seq OWNER TO boac;
ALTER SEQUENCE cohort_filter_events_id_seq OWNED BY cohort_filter_events.id;
ALTER TABLE ONLY cohort_filter_events ALTER COLUMN id SET DEFAULT nextval('cohort_filter_events_id_seq'::regclass);
ALTER TABLE ONLY cohort_filter_events
    ADD CONSTRAINT cohort_filter_events_pkey PRIMARY KEY (id);

CREATE INDEX cohort_filter_events_cohort_filter_id_idx ON cohort_filter_events USING btree (cohort_filter_id);
CREATE INDEX cohort_filter_events_sid_idx ON cohort_filter_events USING btree (sid);
CREATE INDEX cohort_filter_events_event_type_idx ON cohort_filter_events USING btree (event_type);
CREATE INDEX cohort_filter_events_created_at_idx ON cohort_filter_events USING btree (created_at);

--

CREATE TYPE cohort_domain_types AS ENUM ('default', 'admitted_students');

--

CREATE TABLE cohort_filters (
    id integer NOT NULL,
    owner_id integer NOT NULL,
    domain cohort_domain_types NOT NULL,
    name character varying(255) NOT NULL,
    filter_criteria jsonb NOT NULL,
    sids VARCHAR(80)[],
    student_count integer,
    alert_count integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
ALTER TABLE cohort_filters OWNER TO boac;
CREATE SEQUENCE cohort_filters_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE cohort_filters_id_seq OWNER TO boac;
ALTER SEQUENCE cohort_filters_id_seq OWNED BY cohort_filters.id;
ALTER TABLE ONLY cohort_filters ALTER COLUMN id SET DEFAULT nextval('cohort_filters_id_seq'::regclass);
ALTER TABLE ONLY cohort_filters
    ADD CONSTRAINT cohort_filters_pkey PRIMARY KEY (id);
CREATE INDEX cohort_filters_owner_id_idx ON cohort_filters USING btree (owner_id);

--

CREATE TABLE degree_progress_category_unit_requirements (
  category_id INTEGER,
  unit_requirement_id INTEGER
);
ALTER TABLE degree_progress_category_unit_requirements OWNER TO boac;
ALTER TABLE ONLY degree_progress_category_unit_requirements
    ADD CONSTRAINT degree_progress_category_unit_requirements_pkey PRIMARY KEY (category_id, unit_requirement_id);

--


CREATE TABLE degree_progress_course_unit_requirements (
  course_id INTEGER,
  unit_requirement_id INTEGER
);
ALTER TABLE degree_progress_course_unit_requirements OWNER TO boac;
ALTER TABLE ONLY degree_progress_course_unit_requirements
    ADD CONSTRAINT degree_progress_course_unit_requirements_pkey PRIMARY KEY (course_id, unit_requirement_id);

--


CREATE TABLE degree_progress_templates (
  id integer NOT NULL,
  degree_name character varying(255) NOT NULL,
  advisor_dept_codes character varying[] NOT NULL,
  parent_template_id integer,
  student_sid character varying(80),
  created_at timestamp with time zone NOT NULL,
  created_by integer NOT NULL,
  updated_at timestamp with time zone NOT NULL,
  updated_by integer NOT NULL,
  deleted_at timestamp with time zone
);
ALTER TABLE degree_progress_templates OWNER TO boac;
CREATE SEQUENCE degree_progress_templates_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE degree_progress_templates_id_seq OWNER TO boac;
ALTER SEQUENCE degree_progress_templates_id_seq OWNED BY degree_progress_templates.id;
ALTER TABLE ONLY degree_progress_templates ALTER COLUMN id SET DEFAULT nextval('degree_progress_templates_id_seq'::regclass);
ALTER TABLE ONLY degree_progress_templates
    ADD CONSTRAINT degree_progress_templates_pkey PRIMARY KEY (id);
ALTER TABLE ONLY degree_progress_templates
  ADD CONSTRAINT degree_progress_templates_parent_template_id_fkey FOREIGN KEY (parent_template_id) REFERENCES degree_progress_templates(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_templates
    ADD CONSTRAINT degree_progress_templates_created_by_fkey FOREIGN KEY (created_by) REFERENCES authorized_users(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_templates
    ADD CONSTRAINT degree_progress_templates_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES authorized_users(id) ON DELETE CASCADE;

--

CREATE TYPE degree_progress_category_types AS ENUM (
    'Category',
    'Subcategory',
    'Course Requirement',
    'Placeholder: Course Copy',
    'Campus Requirement, Unsatisfied',
    'Campus Requirement, Satisfied'
);

CREATE TABLE degree_progress_categories (
    id integer NOT NULL,
    accent_color VARCHAR(255),
    category_type degree_progress_category_types NOT NULL,
    course_units numrange,
    description text,
    grade VARCHAR(50),
    is_ignored BOOLEAN DEFAULT false NOT NULL,
    is_recommended BOOLEAN DEFAULT false NOT NULL,
    is_satisfied_by_transfer_course BOOLEAN DEFAULT false NOT NULL,
    name character varying(255) NOT NULL,
    note TEXT,
    parent_category_id integer,
    position integer NOT NULL,
    template_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
ALTER TABLE degree_progress_categories OWNER TO boac;
CREATE SEQUENCE degree_progress_categories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE degree_progress_categories_id_seq OWNER TO boac;
ALTER SEQUENCE degree_progress_categories_id_seq OWNED BY degree_progress_categories.id;
ALTER TABLE ONLY degree_progress_categories ALTER COLUMN id SET DEFAULT nextval('degree_progress_categories_id_seq'::regclass);
ALTER TABLE ONLY degree_progress_categories
    ADD CONSTRAINT degree_progress_categories_pkey PRIMARY KEY (id);
ALTER TABLE ONLY degree_progress_categories
    ADD CONSTRAINT degree_progress_categories_parent_category_id_fkey FOREIGN KEY (parent_category_id) REFERENCES degree_progress_categories(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_categories
    ADD CONSTRAINT degree_progress_categories_template_id_fkey FOREIGN KEY (template_id) REFERENCES degree_progress_templates(id) ON DELETE CASCADE;
CREATE INDEX degree_progress_categories_id_idx ON degree_progress_categories USING btree (template_id);

--

CREATE TABLE degree_progress_courses (
  id integer NOT NULL,
  accent_color VARCHAR(255),
  category_id INTEGER,
  degree_check_id INTEGER,
  display_name VARCHAR(255) NOT NULL,
  grade VARCHAR(50) NOT NULL,
  ignore BOOLEAN NOT NULL,
  manually_created_at TIMESTAMP WITH TIME ZONE,
  manually_created_by INTEGER,
  note text,
  section_id INTEGER,
  sid VARCHAR(80) NOT NULL,
  term_id INTEGER,
  units NUMERIC,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE degree_progress_courses OWNER TO boac;
CREATE SEQUENCE degree_progress_courses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE degree_progress_courses_id_seq OWNER TO boac;
ALTER SEQUENCE degree_progress_courses_id_seq OWNED BY degree_progress_courses.id;
ALTER TABLE ONLY degree_progress_courses ALTER COLUMN id SET DEFAULT nextval('degree_progress_courses_id_seq'::regclass);
ALTER TABLE ONLY degree_progress_courses
    ADD CONSTRAINT degree_progress_courses_pkey PRIMARY KEY (id);
ALTER TABLE ONLY degree_progress_courses
    ADD CONSTRAINT degree_progress_courses_manually_created_by_fkey
    FOREIGN KEY (manually_created_by) REFERENCES authorized_users(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_courses
    ADD CONSTRAINT degree_progress_courses_category_id_course_unique_constraint
    UNIQUE (category_id, degree_check_id, display_name, section_id, sid, term_id);

--

CREATE TABLE degree_progress_notes (
  template_id integer NOT NULL,
  body text NOT NULL,
  created_at timestamp with time zone NOT NULL,
  updated_at timestamp with time zone NOT NULL,
  updated_by integer NOT NULL
);
ALTER TABLE degree_progress_notes OWNER TO boac;
ALTER TABLE ONLY degree_progress_notes
    ADD CONSTRAINT degree_progress_notes_pkey PRIMARY KEY (template_id);
ALTER TABLE ONLY degree_progress_notes
    ADD CONSTRAINT degree_progress_notes_template_id_fkey FOREIGN KEY (template_id) REFERENCES degree_progress_templates(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_notes
    ADD CONSTRAINT degree_progress_notes_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES authorized_users(id) ON DELETE CASCADE;


--


CREATE TABLE degree_progress_unit_requirements (
  id integer NOT NULL,
  template_id integer NOT NULL,
  name character varying(255) NOT NULL,
  min_units NUMERIC NOT NULL,
  created_at timestamp with time zone NOT NULL,
  created_by integer NOT NULL,
  updated_at timestamp with time zone NOT NULL,
  updated_by integer NOT NULL
);
ALTER TABLE degree_progress_unit_requirements OWNER TO boac;
CREATE SEQUENCE degree_progress_unit_requirements_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE degree_progress_unit_requirements_id_seq OWNER TO boac;
ALTER SEQUENCE degree_progress_unit_requirements_id_seq OWNED BY degree_progress_unit_requirements.id;
ALTER TABLE ONLY degree_progress_unit_requirements ALTER COLUMN id SET DEFAULT nextval('degree_progress_unit_requirements_id_seq'::regclass);
ALTER TABLE ONLY degree_progress_unit_requirements
    ADD CONSTRAINT degree_progress_unit_requirements_pkey PRIMARY KEY (id);
ALTER TABLE ONLY degree_progress_unit_requirements
    ADD CONSTRAINT degree_progress_unit_requirements_template_id_fkey FOREIGN KEY (template_id) REFERENCES degree_progress_templates(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_unit_requirements
    ADD CONSTRAINT degree_progress_unit_requirements_created_by_fkey FOREIGN KEY (created_by) REFERENCES authorized_users(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_unit_requirements
    ADD CONSTRAINT degree_progress_unit_requirements_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES authorized_users(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_unit_requirements
    ADD CONSTRAINT degree_progress_unit_requirements_name_template_id_unique_const UNIQUE (name, template_id);
CREATE INDEX degree_progress_unit_requirements_template_id_idx ON degree_progress_unit_requirements (template_id);

--

CREATE TABLE notes_read (
    note_id character varying(255) NOT NULL,
    viewer_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL
);
ALTER TABLE notes_read OWNER TO boac;
ALTER TABLE ONLY notes_read
    ADD CONSTRAINT notes_read_pkey PRIMARY KEY (viewer_id, note_id);
CREATE INDEX notes_read_note_id_idx ON notes_read USING btree (note_id);
CREATE INDEX notes_read_viewer_id_idx ON notes_read USING btree (viewer_id);

--

CREATE TYPE note_contact_types AS ENUM (
    'Email',
    'Phone',
    'Online same day',
    'Online scheduled',
    'In-person same day',
    'In-person scheduled',
    'Group event',
    'Admin'
);

CREATE TABLE notes (
    id INTEGER NOT NULL,
    author_uid VARCHAR(255) NOT NULL,
    author_name VARCHAR(255) NOT NULL,
    author_role VARCHAR(255) NOT NULL,
    author_dept_codes VARCHAR[] NOT NULL,
    body TEXT,
    contact_type note_contact_types,
    is_draft BOOLEAN DEFAULT FALSE NOT NULL,
    is_private BOOLEAN DEFAULT FALSE NOT NULL,
    set_date DATE,
    sid VARCHAR(80),
    subject VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);
ALTER TABLE notes OWNER TO boac;
CREATE SEQUENCE notes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE notes_id_seq OWNER TO boac;
ALTER SEQUENCE notes_id_seq OWNED BY notes.id;
ALTER TABLE ONLY notes ALTER COLUMN id SET DEFAULT nextval('notes_id_seq'::regclass);
ALTER TABLE ONLY notes ADD CONSTRAINT notes_pkey PRIMARY KEY (id);
CREATE INDEX notes_author_uid_idx ON notes USING btree (author_uid);
CREATE INDEX notes_deleted_at_idx ON notes (deleted_at);
CREATE INDEX notes_is_private_idx ON notes (is_private);
CREATE INDEX notes_sid_idx ON notes USING btree (sid);

CREATE MATERIALIZED VIEW notes_fts_index AS (
  SELECT
    id,
    CASE WHEN (body IS NULL OR is_private) THEN to_tsvector('english', subject)
         ELSE to_tsvector('english', subject || ' ' || body)
         END AS fts_index
  FROM notes
  WHERE deleted_at IS NULL AND is_draft IS FALSE
);

CREATE INDEX idx_notes_fts_index
ON notes_fts_index
USING gin(fts_index);

--

CREATE MATERIALIZED VIEW advisor_author_index AS (
  SELECT DISTINCT author_name AS advisor_name, author_uid AS advisor_uid
  FROM notes
  ORDER BY advisor_name
);

CREATE INDEX idx_advisor_author_index ON advisor_author_index USING btree(advisor_name);

--

CREATE TABLE note_attachments (
    id integer NOT NULL,
    note_id INTEGER NOT NULL,
    path_to_attachment character varying(255) NOT NULL,
    uploaded_by_uid character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone
);
ALTER TABLE note_attachments OWNER TO boac;
CREATE SEQUENCE note_attachments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE note_attachments_id_seq OWNER TO boac;
ALTER SEQUENCE note_attachments_id_seq OWNED BY note_attachments.id;
ALTER TABLE ONLY note_attachments ALTER COLUMN id SET DEFAULT nextval('note_attachments_id_seq'::regclass);
ALTER TABLE ONLY note_attachments
    ADD CONSTRAINT note_attachments_pkey PRIMARY KEY (id);
ALTER TABLE ONLY note_attachments
    ADD CONSTRAINT note_attachments_note_id_path_to_attachment_unique_constraint UNIQUE (note_id, path_to_attachment, deleted_at);
CREATE INDEX note_attachments_note_id_idx ON note_attachments USING btree (note_id);

--

CREATE TABLE note_templates (
    id INTEGER NOT NULL,
    body text,
    creator_id INTEGER NOT NULL,
    is_private BOOLEAN DEFAULT FALSE NOT NULL,
    subject VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);
ALTER TABLE note_templates OWNER TO boac;
CREATE SEQUENCE note_templates_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE note_templates_id_seq OWNER TO boac;
ALTER SEQUENCE note_templates_id_seq OWNED BY note_templates.id;
ALTER TABLE ONLY note_templates ALTER COLUMN id SET DEFAULT nextval('note_templates_id_seq'::regclass);
ALTER TABLE ONLY note_templates ADD CONSTRAINT note_templates_pkey PRIMARY KEY (id);
ALTER TABLE ONLY note_templates
    ADD CONSTRAINT note_templates_creator_id_title_unique_constraint UNIQUE (creator_id, title, deleted_at);
CREATE INDEX note_templates_creator_id_idx ON note_templates USING btree (creator_id);

--

CREATE TABLE note_template_attachments (
    id integer NOT NULL,
    note_template_id INTEGER NOT NULL,
    path_to_attachment character varying(255) NOT NULL,
    uploaded_by_uid character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone
);
ALTER TABLE note_template_attachments OWNER TO boac;
CREATE SEQUENCE note_template_attachments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE note_template_attachments_id_seq OWNER TO boac;
ALTER SEQUENCE note_template_attachments_id_seq OWNED BY note_template_attachments.id;
ALTER TABLE ONLY note_template_attachments ALTER COLUMN id SET DEFAULT nextval('note_template_attachments_id_seq'::regclass);
ALTER TABLE ONLY note_template_attachments
    ADD CONSTRAINT note_template_attachments_pkey PRIMARY KEY (id);
ALTER TABLE ONLY note_template_attachments
    ADD CONSTRAINT nta_note_template_id_path_to_attachment_unique_constraint UNIQUE (note_template_id, path_to_attachment);
CREATE INDEX note_template_attachments_note_template_id_idx ON note_template_attachments USING btree (note_template_id);

--

CREATE TABLE note_template_topics (
    id INTEGER NOT NULL,
    note_template_id INTEGER NOT NULL,
    topic VARCHAR(50) NOT NULL
);
ALTER TABLE note_template_topics OWNER TO boac;
CREATE SEQUENCE note_template_topics_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE note_template_topics_id_seq OWNER TO boac;
ALTER SEQUENCE note_template_topics_id_seq OWNED BY note_template_topics.id;
ALTER TABLE ONLY note_template_topics ALTER COLUMN id SET DEFAULT nextval('note_template_topics_id_seq'::regclass);
ALTER TABLE ONLY note_template_topics
    ADD CONSTRAINT note_template_topics_pkey PRIMARY KEY (id);
ALTER TABLE ONLY note_template_topics
    ADD CONSTRAINT note_template_topics_note_template_id_topic_unique_constraint UNIQUE (note_template_id, topic);
CREATE INDEX note_template_topics_note_template_id_idx ON note_template_topics (note_template_id);

--

CREATE TABLE note_topics (
    id INTEGER NOT NULL,
    note_id INTEGER NOT NULL,
    topic VARCHAR(50) NOT NULL,
    author_uid VARCHAR(255) NOT NULL,
    deleted_at timestamp with time zone
);
ALTER TABLE note_topics OWNER TO boac;
CREATE SEQUENCE note_topics_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE note_topics_id_seq OWNER TO boac;
ALTER SEQUENCE note_topics_id_seq OWNED BY note_topics.id;
ALTER TABLE ONLY note_topics ALTER COLUMN id SET DEFAULT nextval('note_topics_id_seq'::regclass);
ALTER TABLE ONLY note_topics
    ADD CONSTRAINT note_topics_pkey PRIMARY KEY (id);
ALTER TABLE ONLY note_topics
    ADD CONSTRAINT note_topics_note_id_topic_unique_constraint UNIQUE (note_id, topic, deleted_at);
CREATE INDEX note_topics_note_id_idx ON note_topics (note_id);
CREATE INDEX note_topics_topic_idx ON note_topics (topic);

--

CREATE TABLE student_groups (
  id INTEGER NOT NULL,
  domain cohort_domain_types NOT NULL,
  name VARCHAR(255) NOT NULL,
  owner_id INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE student_groups OWNER TO boac;
CREATE SEQUENCE student_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE student_groups_id_seq OWNER TO boac;
ALTER SEQUENCE student_groups_id_seq OWNED BY student_groups.id;
ALTER TABLE ONLY student_groups ALTER COLUMN id SET DEFAULT nextval('student_groups_id_seq'::regclass);
ALTER TABLE ONLY student_groups
    ADD CONSTRAINT student_groups_pkey PRIMARY KEY (id);
ALTER TABLE ONLY student_groups
    ADD CONSTRAINT student_groups_owner_id_name_unique_constraint UNIQUE (owner_id, name);
CREATE INDEX student_groups_owner_id_idx ON student_groups USING btree (owner_id);

--

CREATE TABLE student_group_members (
  student_group_id INTEGER,
  sid VARCHAR(80) NOT NULL
);
ALTER TABLE student_group_members OWNER TO boac;
ALTER TABLE ONLY student_group_members
    ADD CONSTRAINT student_group_members_pkey PRIMARY KEY (student_group_id, sid);
CREATE INDEX student_group_members_student_group_id_idx ON student_group_members USING btree (student_group_id);
CREATE INDEX student_group_members_sid_idx ON student_group_members USING btree (sid);

--

CREATE TABLE topics (
  id INTEGER NOT NULL,
  topic VARCHAR(50) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  deleted_at timestamp with time zone
);
ALTER TABLE topics OWNER TO boac;
CREATE SEQUENCE topics_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE topics_id_seq OWNER TO boac;
ALTER SEQUENCE topics_id_seq OWNED BY topics.id;
ALTER TABLE ONLY topics ALTER COLUMN id SET DEFAULT nextval('topics_id_seq'::regclass);
ALTER TABLE ONLY topics
    ADD CONSTRAINT topics_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY topics
    ADD CONSTRAINT topics_topic_unique_constraint UNIQUE (topic);

--

CREATE TABLE university_depts (
  id INTEGER NOT NULL,
  dept_code VARCHAR(80) NOT NULL,
  dept_name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE university_depts OWNER TO boac;
CREATE SEQUENCE university_depts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE university_depts_id_seq OWNER TO boac;
ALTER SEQUENCE university_depts_id_seq OWNED BY university_depts.id;
ALTER TABLE ONLY university_depts ALTER COLUMN id SET DEFAULT nextval('university_depts_id_seq'::regclass);
ALTER TABLE ONLY university_depts
    ADD CONSTRAINT university_depts_pkey PRIMARY KEY (id);
ALTER TABLE ONLY university_depts
    ADD CONSTRAINT university_depts_code_unique_constraint UNIQUE (dept_code, dept_name);

--

CREATE TYPE university_dept_member_role_types AS ENUM ('advisor', 'director');

--

CREATE TABLE university_dept_members (
  university_dept_id INTEGER,
  authorized_user_id INTEGER,
  role university_dept_member_role_types,
  automate_membership boolean DEFAULT true NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE university_dept_members OWNER TO boac;
ALTER TABLE ONLY university_dept_members
    ADD CONSTRAINT university_dept_members_pkey PRIMARY KEY (university_dept_id, authorized_user_id);

--

CREATE TABLE peer_advising_departments (
  id integer NOT NULL,
  name character varying(255) NOT NULL,
  university_dept_id integer NOT NULL,
  created_at timestamp with time zone NOT NULL,
  updated_at timestamp with time zone NOT NULL
);

ALTER TABLE peer_advising_departments OWNER TO boac;
CREATE SEQUENCE peer_advising_departments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE peer_advising_departments_id_seq OWNER TO boac;
ALTER SEQUENCE peer_advising_departments_id_seq OWNED BY peer_advising_departments.id;
ALTER TABLE ONLY peer_advising_departments ALTER COLUMN id SET DEFAULT nextval('peer_advising_departments_id_seq'::regclass);
ALTER TABLE ONLY peer_advising_departments
    ADD CONSTRAINT peer_advising_departments_pkey PRIMARY KEY (id);
ALTER TABLE ONLY peer_advising_departments
    ADD CONSTRAINT peer_advising_departments_university_dept_id_fkey FOREIGN KEY (university_dept_id) REFERENCES university_depts(id) ON DELETE CASCADE;

CREATE INDEX peer_advising_departments_university_dept_id_idx ON peer_advising_departments(university_dept_id);

--

CREATE TYPE role_type_enum AS ENUM ('peer_advisor', 'peer_advisor_manager');

CREATE TABLE IF NOT EXISTS peer_advising_department_members (
  peer_advising_department_id integer NOT NULL,
  authorized_user_id integer NOT NULL,
  role_type role_type_enum NOT NULL,
  created_at timestamp with time zone NOT NULL,
  updated_at timestamp with time zone NOT NULL,
  deleted_at timestamp with time zone
);

ALTER TABLE peer_advising_department_members OWNER TO boac;

ALTER TABLE ONLY peer_advising_department_members
    DROP CONSTRAINT IF EXISTS peer_advising_department_members_pkey;
ALTER TABLE peer_advising_department_members
    ADD CONSTRAINT peer_advising_department_members_pkey PRIMARY KEY (peer_advising_department_id, authorized_user_id);

ALTER TABLE ONLY peer_advising_department_members
    DROP CONSTRAINT IF EXISTS peer_advising_department_members_peer_advising_department_id_fkey;
ALTER TABLE ONLY peer_advising_department_members
    ADD CONSTRAINT peer_advising_department_members_peer_advising_department_id_fkey FOREIGN KEY (peer_advising_department_id) REFERENCES peer_advising_departments(id) ON DELETE CASCADE;

ALTER TABLE ONLY peer_advising_department_members
    DROP CONSTRAINT IF EXISTS peer_advising_department_members_authorized_user_id_fkey;
ALTER TABLE ONLY peer_advising_department_members
    ADD CONSTRAINT peer_advising_department_members_authorized_user_id_fkey FOREIGN KEY (authorized_user_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

--

CREATE TABLE json_cache (
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    id integer NOT NULL,
    key character varying NOT NULL,
    json jsonb
);
ALTER TABLE json_cache OWNER TO boac;
CREATE SEQUENCE json_cache_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE json_cache_id_seq OWNER TO boac;
ALTER SEQUENCE json_cache_id_seq OWNED BY json_cache.id;
ALTER TABLE ONLY json_cache ALTER COLUMN id SET DEFAULT nextval('json_cache_id_seq'::regclass);
ALTER TABLE ONLY json_cache
    ADD CONSTRAINT json_cache_key_key UNIQUE (key);
ALTER TABLE ONLY json_cache
    ADD CONSTRAINT json_cache_pkey PRIMARY KEY (id);

--

CREATE TABLE tool_settings (
    id integer NOT NULL,
    key character varying NOT NULL,
    value text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
ALTER TABLE tool_settings OWNER TO boac;
CREATE SEQUENCE tool_settings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE tool_settings_id_seq OWNER TO boac;
ALTER SEQUENCE tool_settings_id_seq OWNED BY tool_settings.id;
ALTER TABLE ONLY tool_settings ALTER COLUMN id SET DEFAULT nextval('tool_settings_id_seq'::regclass);
ALTER TABLE ONLY tool_settings
    ADD CONSTRAINT tool_settings_key_unique_constraint UNIQUE (key);
ALTER TABLE ONLY tool_settings
    ADD CONSTRAINT tool_settings_pkey PRIMARY KEY (id);
CREATE INDEX tool_settings_key_idx ON tool_settings USING btree (key);

--

CREATE TABLE user_logins(
    id integer NOT NULL,
    uid character varying NOT NULL,
    created_at timestamp with time zone NOT NULL
);
CREATE SEQUENCE user_logins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE user_logins_id_seq OWNER TO boac;
ALTER SEQUENCE user_logins_id_seq OWNED BY user_logins.id;
ALTER TABLE ONLY user_logins ALTER COLUMN id SET DEFAULT nextval('user_logins_id_seq'::regclass);
ALTER TABLE ONLY user_logins
    ADD CONSTRAINT user_logins_pkey PRIMARY KEY (id);
CREATE INDEX user_logins_uid_idx ON user_logins USING btree (uid);


--

ALTER TABLE ONLY appointments_read
    ADD CONSTRAINT appointments_read_viewer_id_fkey FOREIGN KEY (viewer_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY cohort_filters
    ADD CONSTRAINT cohort_filters_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY degree_progress_category_unit_requirements
    ADD CONSTRAINT degree_progress_category_unit_reqts_category_id_fkey
    FOREIGN KEY (category_id) REFERENCES degree_progress_categories(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_category_unit_requirements
    ADD CONSTRAINT degree_progress_category_unit_reqts_unit_requirement_id_fkey
    FOREIGN KEY (unit_requirement_id) REFERENCES degree_progress_unit_requirements(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY degree_progress_course_unit_requirements
    ADD CONSTRAINT degree_progress_course_unit_reqts_course_id_fkey
    FOREIGN KEY (course_id) REFERENCES degree_progress_courses(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_course_unit_requirements
    ADD CONSTRAINT degree_progress_course_unit_reqts_unit_requirement_id_fkey
    FOREIGN KEY (unit_requirement_id) REFERENCES degree_progress_unit_requirements(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY degree_progress_courses
    ADD CONSTRAINT degree_progress_courses_category_id_fkey
    FOREIGN KEY (category_id) REFERENCES degree_progress_categories(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_courses
    ADD CONSTRAINT degree_progress_courses_degree_check_id_fkey
    FOREIGN KEY (degree_check_id) REFERENCES degree_progress_templates(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY student_group_members
    ADD CONSTRAINT student_group_members_student_group_id_fkey FOREIGN KEY (student_group_id) REFERENCES student_groups(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY student_groups
    ADD CONSTRAINT student_groups_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY user_logins
    ADD CONSTRAINT user_logins_uid_fkey FOREIGN KEY (uid) REFERENCES authorized_users(uid) ON DELETE CASCADE;

--

ALTER TABLE ONLY university_dept_members
    ADD CONSTRAINT university_dept_members_university_dept_id_fkey FOREIGN KEY (university_dept_id) REFERENCES university_depts(id) ON DELETE CASCADE;
ALTER TABLE ONLY university_dept_members
    ADD CONSTRAINT university_dept_members_authorized_user_id_fkey FOREIGN KEY (authorized_user_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY alert_views
    ADD CONSTRAINT alert_views_alert_id_fkey FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE;
ALTER TABLE ONLY alert_views
    ADD CONSTRAINT alert_views_viewer_id_fkey FOREIGN KEY (viewer_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY cohort_filter_events
    ADD CONSTRAINT cohort_filter_events_cohort_filter_id_fkey FOREIGN KEY (cohort_filter_id) REFERENCES cohort_filters(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY notes_read
    ADD CONSTRAINT notes_read_viewer_id_fkey FOREIGN KEY (viewer_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY note_attachments
    ADD CONSTRAINT note_attachments_note_id_fkey FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY note_templates
    ADD CONSTRAINT note_templates_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY note_template_attachments
    ADD CONSTRAINT note_template_attachments_note_template_id_fkey FOREIGN KEY (note_template_id) REFERENCES note_templates(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY note_template_topics
    ADD CONSTRAINT note_template_topics_note_template_id_fkey FOREIGN KEY (note_template_id) REFERENCES note_templates(id) ON DELETE CASCADE;

--

ALTER TABLE ONLY note_topics
    ADD CONSTRAINT note_topics_note_id_fkey FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE;

ALTER TABLE ONLY note_topics
    ADD CONSTRAINT note_topics_author_uid_fkey FOREIGN KEY (author_uid) REFERENCES authorized_users(uid) ON DELETE CASCADE;


