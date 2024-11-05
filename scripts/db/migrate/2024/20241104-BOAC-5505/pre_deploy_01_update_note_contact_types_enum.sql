BEGIN;

ALTER TYPE note_contact_types RENAME VALUE 'In person scheduled' TO 'In-person scheduled';

ALTER TYPE note_contact_types ADD VALUE 'Group event' AFTER 'In-person scheduled';

COMMIT;
