-- DROP SEQUENCE IF EXISTS urls_id_seq CASCADE;
-- DROP SEQUENCE IF EXISTS url_checks_id_seq CASCADE;
-- DROP TABLE IF EXISTS urls CASCADE;
-- DROP TABLE IF EXISTS url_checks CASCADE;
DO $$ 
BEGIN
   IF EXISTS (SELECT 1 FROM pg_class WHERE relname = 'urls_id_seq') THEN
      DROP SEQUENCE urls_id_seq CASCADE;
   END IF;
   IF EXISTS (SELECT 1 FROM pg_class WHERE relname = 'url_checks_id_seq') THEN
      DROP SEQUENCE url_checks_id_seq CASCADE;
   END IF;
   IF EXISTS (SELECT 1 FROM pg_class WHERE relname = 'urls') THEN
      DROP TABLE urls CASCADE;
   END IF;
   IF EXISTS (SELECT 1 FROM pg_class WHERE relname = 'url_checks') THEN
      DROP TABLE url_checks CASCADE;
   END IF;
END $$;


CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS url_checks (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id INTEGER REFERENCES urls(id) ON DELETE CASCADE,
    status_code INTEGER,
    h1 TEXT,
    title TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);