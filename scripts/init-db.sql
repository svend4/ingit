-- PostgreSQL initialization script
-- This script is run when the database container is first created

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- Create schema
CREATE SCHEMA IF NOT EXISTS ingit;

-- Set search path
SET search_path TO ingit, public;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA ingit TO ingit;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ingit TO ingit;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ingit TO ingit;

-- Create initial database comment
COMMENT ON SCHEMA ingit IS 'InGit application schema';

-- Optional: Create read-only user for reporting
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'ingit_readonly') THEN
        CREATE USER ingit_readonly WITH PASSWORD 'readonly';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE ingit TO ingit_readonly;
GRANT USAGE ON SCHEMA ingit TO ingit_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA ingit TO ingit_readonly;
