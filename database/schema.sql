CREATE DATABASE IF NOT EXISTS krishimitra CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE krishimitra;
CREATE TABLE farmers (
  farmer_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  display_name VARCHAR(120),
  preferred_language VARCHAR(20) DEFAULT 'hi',
  district VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE diagnosis_history (
  diagnosis_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  farmer_id BIGINT NULL,
  crop_name VARCHAR(100),
  predicted_class VARCHAR(180) NOT NULL,
  confidence DECIMAL(6,5),
  image_path VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id) ON DELETE SET NULL
);
CREATE TABLE assistant_queries (
  query_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  farmer_id BIGINT NULL,
  query_text TEXT NOT NULL,
  response_text TEXT,
  language_code VARCHAR(20) DEFAULT 'hi',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id) ON DELETE SET NULL
);
