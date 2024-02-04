
DROP TABLE IF EXISTS Users CASCADE;
CREATE TABLE Users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  first_name VARCHAR(255) NOT NULL,
  last_name VARCHAR(255) NOT NULL,
  password VARCHAR(255),
  auth_type VARCHAR(255) NOT NULL DEFAULT 'local'
);

ALTER TABLE Users
-- ADD COLUMN auth_type VARCHAR(255) NOT NULL DEFAULT 'local',
ADD CONSTRAINT auth_type_check CHECK (auth_type IN ('local', 'sso'));