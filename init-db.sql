-- Initialize Bottleplug Database
-- This file runs automatically when the PostgreSQL container starts for the first time

-- Create additional database if needed
-- CREATE DATABASE bottleplug_test;

-- Grant permissions (if using custom users)
-- GRANT ALL PRIVILEGES ON DATABASE bottleplug TO postgres;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: Tables will be created by Django migrations
-- This file is mainly for initial setup and extensions
