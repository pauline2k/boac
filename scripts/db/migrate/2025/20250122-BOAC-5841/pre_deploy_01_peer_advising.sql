BEGIN;

ALTER TABLE authorized_users ADD COLUMN IF NOT EXISTS is_peer_advisor BOOLEAN DEFAULT FALSE NOT NULL;

CREATE TABLE IF NOT EXISTS peer_advising_departments (
  id integer NOT NULL,
  name character varying(255) NOT NULL,
  university_dept_id integer NOT NULL,
  created_at timestamp with time zone NOT NULL,
  updated_at timestamp with time zone NOT NULL
);

ALTER TABLE peer_advising_departments OWNER TO boac;
CREATE SEQUENCE IF NOT EXISTS peer_advising_departments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE peer_advising_departments_id_seq OWNER TO boac;
ALTER SEQUENCE peer_advising_departments_id_seq OWNED BY peer_advising_departments.id;
ALTER TABLE ONLY peer_advising_departments ALTER COLUMN id SET DEFAULT nextval('peer_advising_departments_id_seq'::regclass);

ALTER TABLE ONLY peer_advising_departments
    DROP CONSTRAINT IF EXISTS peer_advising_departments_pkey;
ALTER TABLE ONLY peer_advising_departments
    ADD CONSTRAINT peer_advising_departments_pkey PRIMARY KEY (id);

ALTER TABLE ONLY peer_advising_departments
    DROP CONSTRAINT IF EXISTS peer_advising_departments_university_dept_id_fkey;
ALTER TABLE ONLY peer_advising_departments
    ADD CONSTRAINT peer_advising_departments_university_dept_id_fkey FOREIGN KEY (university_dept_id) REFERENCES university_depts(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS peer_advising_departments_university_dept_id_idx ON peer_advising_departments(university_dept_id);

COMMIT;