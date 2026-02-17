DROP DATABASE IF EXISTS real_estate_db;
CREATE DATABASE real_estate_db;
USE real_estate_db;

CREATE TABLE agents (
    Agent_ID VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(100),
    Phone VARCHAR(20),
    Email VARCHAR(100)
) ENGINE=InnoDB;

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
    FOREIGN KEY (Agent_ID)
        REFERENCES agents(Agent_ID)
) ENGINE=InnoDB;

CREATE TABLE agents_enhanced (
    agent_id VARCHAR(10) PRIMARY KEY,
    commission_rate DECIMAL(4,2),
    deals_closed INT,
    rating DECIMAL(2,1),
    experience_years INT,
    avg_closing_days INT,
    FOREIGN KEY (agent_id)
        REFERENCES agents(Agent_ID)
) ENGINE=InnoDB;

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
    FOREIGN KEY (listing_id)
        REFERENCES listings(Listing_ID)
) ENGINE=InnoDB;

CREATE TABLE sales (
    Listing_ID VARCHAR(10) PRIMARY KEY,
    Sale_Price DECIMAL(14,2),
    Date_Sold DATE,
    Days_on_Market DECIMAL(6,2),
    FOREIGN KEY (Listing_ID)
        REFERENCES listings(Listing_ID)
) ENGINE=InnoDB;

CREATE TABLE buyers (
    buyer_id INT,
    sale_id VARCHAR(10),
    buyer_type VARCHAR(50),
    payment_mode VARCHAR(20),
    loan_taken BOOLEAN,
    loan_provider VARCHAR(100),
    loan_amount DECIMAL(12,2),
    PRIMARY KEY (buyer_id, sale_id),
    FOREIGN KEY (sale_id)
        REFERENCES listings(Listing_ID)
) ENGINE=InnoDB;
show tables;
SET FOREIGN_KEY_CHECKS = 0;
CREATE TABLE temp_json (
    data JSON
);
LOAD DATA INFILE 'B:\Job\GUVI\Project\Dataset\agents_20k.json'
INTO TABLE temp_json;

INSERT INTO agents (Agent_ID, Name, Phone, Email)
SELECT 
    JSON_UNQUOTE(JSON_EXTRACT(data, '$.Agent_ID')),
    JSON_UNQUOTE(JSON_EXTRACT(data, '$.Name')),
    JSON_UNQUOTE(JSON_EXTRACT(data, '$.Phone')),
    JSON_UNQUOTE(JSON_EXTRACT(data, '$.Email'))
FROM temp_json;
