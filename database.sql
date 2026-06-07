-- Create Database Tables for Weather App

-- Locations Table: Stores village/mandal/district information
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    village_name TEXT NOT NULL,
    mandal_name TEXT,
    district_name TEXT,
    state_name TEXT,
    country TEXT DEFAULT 'India',
    latitude REAL,
    longitude REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weather History Table: Stores past weather searches
CREATE TABLE IF NOT EXISTS weather_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER,
    temperature REAL,
    feels_like REAL,
    humidity INTEGER,
    wind_speed REAL,
    wind_direction TEXT,
    pressure REAL,
    condition TEXT,
    cloud_cover INTEGER,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

-- Index for faster searches
CREATE INDEX IF NOT EXISTS idx_village_name ON locations(village_name);
CREATE INDEX IF NOT EXISTS idx_mandal_name ON locations(mandal_name);
CREATE INDEX IF NOT EXISTS idx_district_name ON locations(district_name);

-- Sample Data: Andhra Pradesh Villages and Mandals
INSERT INTO locations (village_name, mandal_name, district_name, state_name, country, latitude, longitude) VALUES
('Lakkireddipalle', 'Lakkireddipalle', 'Kadapa', 'Andhra Pradesh', 'India', 14.2333, 78.4333),
('Vempalle', 'Vempalle', 'Kadapa', 'Andhra Pradesh', 'India', 14.4167, 78.4667),
('Proddatur', 'Proddatur', 'Kadapa', 'Andhra Pradesh', 'India', 14.7500, 78.0500),
('Pulivendla', 'Pulivendla', 'Kadapa', 'Andhra Pradesh', 'India', 14.4167, 78.2333),
('Rayachoti', 'Rayachoti', 'Annamayya', 'Andhra Pradesh', 'India', 14.0500, 78.8000),
('Kadapa', 'Kadapa', 'Kadapa', 'Andhra Pradesh', 'India', 14.4667, 78.8167),
('Tirupati', 'Tirupati', 'Chittoor', 'Andhra Pradesh', 'India', 13.6283, 79.4192),
('Kurnool', 'Kurnool', 'Kurnool', 'Andhra Pradesh', 'India', 15.8283, 78.0333),
('Nellore', 'Nellore', 'Sri Potti Sriramulu Nellore', 'Andhra Pradesh', 'India', 14.4500, 79.9833),
('Gudur', 'Gudur', 'Sri Potti Sriramulu Nellore', 'Andhra Pradesh', 'India', 14.1500, 79.8833),
('Rajampet', 'Rajampet', 'Annamayya', 'Andhra Pradesh', 'India', 14.1833, 79.0000),
('Madanapalle', 'Madanapalle', 'Chittoor', 'Andhra Pradesh', 'India', 13.5500, 78.5000),
('Hindupur', 'Hindupur', 'Sri Sathya Sai', 'Andhra Pradesh', 'India', 13.8333, 77.4833),
('Anantapur', 'Anantapur', 'Anantapur', 'Andhra Pradesh', 'India', 14.6833, 77.6000),
('Guntakal', 'Guntakal', 'Anantapur', 'Andhra Pradesh', 'India', 15.1667, 77.3667);

-- Query Examples:

-- Search for a location by village name
-- SELECT * FROM locations WHERE village_name LIKE '%Lakkireddipalle%';

-- Get all locations in a district
-- SELECT * FROM locations WHERE district_name = 'Kadapa';

-- Get weather history for a location
-- SELECT * FROM weather_history WHERE location_id = 1 ORDER BY recorded_at DESC;

-- Count searches by location
-- SELECT l.village_name, COUNT(*) as search_count 
-- FROM weather_history w 
-- JOIN locations l ON w.location_id = l.id 
-- GROUP BY l.id 
-- ORDER BY search_count DESC;