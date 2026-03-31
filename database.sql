-- 🔹 1. Create Database
DROP DATABASE IF EXISTS real_estate_db;
CREATE DATABASE real_estate_db;
USE real_estate_db;

-- 🔹 2. Create Tables

CREATE TABLE agents (
    Agent_ID VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(100),
    Phone VARCHAR(20),
    Email VARCHAR(100)
);

CREATE TABLE listings (
    Listing_ID VARCHAR(10) PRIMARY KEY,
    City VARCHAR(50),
    Property_Type VARCHAR(50),
    Price DECIMAL(15,2),
    Sqft DECIMAL(10,2),
    Date_Listed DATE,
    Agent_ID VARCHAR(10),
    Latitude DECIMAL(10,8),
    Longitude DECIMAL(11,8),
    FOREIGN KEY (Agent_ID) REFERENCES agents(Agent_ID)
);

CREATE TABLE agents_enhanced (
    agent_id VARCHAR(10) PRIMARY KEY,
    commission_rate DECIMAL(4,2),
    deals_closed INT,
    rating DECIMAL(2,1),
    experience_years INT,
    avg_closing_days INT,
    FOREIGN KEY (agent_id) REFERENCES agents(Agent_ID)
);

CREATE TABLE property_attributes (
    attribute_id INT PRIMARY KEY,
    listing_id VARCHAR(10),
    bedrooms INT,
    bathrooms INT,
    floor_number INT,
    total_floors INT,
    year_built YEAR,
    is_rented BOOLEAN,
    tenant_count INT,
    furnishing_status VARCHAR(50),
    metro_distance_km DECIMAL(5,2),
    parking_available BOOLEAN,
    power_backup BOOLEAN,
    FOREIGN KEY (listing_id) REFERENCES listings(Listing_ID)
);

CREATE TABLE sales (
    Listing_ID VARCHAR(10) PRIMARY KEY,
    Sale_Price DECIMAL(14,2),
    Date_Sold DATE,
    Days_on_Market DECIMAL(6,2),
    FOREIGN KEY (Listing_ID) REFERENCES listings(Listing_ID)
);

CREATE TABLE buyers (
    buyer_id INT,
    sale_id VARCHAR(10),
    buyer_type VARCHAR(50),
    payment_mode VARCHAR(20),
    loan_taken BOOLEAN,
    loan_provider VARCHAR(100),
    loan_amount DECIMAL(12,2),
    PRIMARY KEY (buyer_id, sale_id),
    FOREIGN KEY (sale_id) REFERENCES listings(Listing_ID)
);

-- 🔹 3. Temporary Table for CSV Load
DROP TABLE IF EXISTS temp_agents;

CREATE TABLE temp_agents (
    agent_id VARCHAR(10),
    commission_rate FLOAT,
    deals_closed INT,
    rating FLOAT,
    experience_years INT,
    avg_closing_days INT
);

-- 🔹 4. Load CSV File (Make sure file is in Uploads folder)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/cleaned_agents.csv'
INTO TABLE temp_agents
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- 🔹 5. Insert into agents table
INSERT INTO agents (Agent_ID, Name, Phone, Email)
SELECT 
    agent_id,
    'Unknown',
    '0000000000',
    'unknown@mail.com'
FROM temp_agents;

-- 🔹 6. Insert into agents_enhanced table
INSERT INTO agents_enhanced 
(agent_id, commission_rate, deals_closed, rating, experience_years, avg_closing_days)
SELECT 
    agent_id,
    commission_rate,
    deals_closed,
    rating,
    experience_years,
    avg_closing_days
FROM temp_agents;

-- 🔹 7. Create Indexes
CREATE INDEX idx_listing_agent ON listings(Agent_ID);
CREATE INDEX idx_listing_city ON listings(City);
CREATE INDEX idx_listing_price ON listings(Price);
CREATE INDEX idx_property_listing ON property_attributes(listing_id);
CREATE INDEX idx_sale_listing ON sales(Listing_ID);

-- 🔹 8. Create Views

-- View 1: Listings + Agents
CREATE OR REPLACE VIEW view_listings_agents AS
SELECT 
    l.Listing_ID,
    l.City,
    l.Property_Type,
    l.Price,
    l.Sqft,
    l.Date_Listed,
    a.Name AS agent_name
FROM listings l
LEFT JOIN agents a ON l.Agent_ID = a.Agent_ID;

-- View 2: Sales + Listings + Buyers
CREATE OR REPLACE VIEW view_sales_full AS
SELECT 
    s.Listing_ID,
    s.Sale_Price,
    s.Date_Sold,
    l.City,
    l.Price AS listing_price,
    b.buyer_id,
    b.buyer_type,
    b.payment_mode
FROM sales s
LEFT JOIN listings l ON s.Listing_ID = l.Listing_ID
LEFT JOIN buyers b ON s.Listing_ID = b.sale_id;

-- View 3: Listings + Attributes
CREATE OR REPLACE VIEW view_listings_attributes AS
SELECT 
    l.Listing_ID,
    l.City,
    l.Property_Type,
    l.Price,
    l.Sqft,
    p.bedrooms,
    p.bathrooms,
    p.furnishing_status,
    p.parking_available
FROM listings l
LEFT JOIN property_attributes p ON l.Listing_ID = p.listing_id;