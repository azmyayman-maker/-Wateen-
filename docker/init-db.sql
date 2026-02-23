-- =============================================================================
-- Wateen Project - PostgreSQL Initialization Script
-- =============================================================================
-- This script runs automatically when the PostgreSQL container starts for the
-- first time. It sets up extensions and initial configuration.
-- =============================================================================

-- Enable PostGIS extension (required for geospatial features)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable PostGIS topology (optional, for advanced spatial operations)
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Enable fuzzy string matching (useful for search)
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set default timezone
SET TIME ZONE 'UTC';

-- Grant necessary permissions to the application user
-- (Adjust if using a separate read-only user)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO wateen_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO wateen_admin;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Wateen database initialized successfully';
    RAISE NOTICE 'PostGIS version: %', PostGIS_Version();
END
$$;
