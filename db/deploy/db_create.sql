-- Create `keys` table

BEGIN;

CREATE TABLE keys (
    key_id SERIAL,
    email VARCHAR(50) NOT NULL,
    api_key VARCHAR(32) NOT NULL
);

CREATE UNIQUE INDEX zulip_email ON keys (email);

COMMIT;
