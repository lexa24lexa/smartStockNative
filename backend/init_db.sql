CREATE DATABASE IF NOT EXISTS retail_bd;
USE retail_bd;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS REPLENISHMENT_LIST_ITEM;
DROP TABLE IF EXISTS REPLENISHMENT_LIST;
DROP TABLE IF EXISTS REPLENISHMENT_LOG;
DROP TABLE IF EXISTS REPLENISHMENT_FREQUENCY;
DROP TABLE IF EXISTS SALE_LINE;
DROP TABLE IF EXISTS SALE;
DROP TABLE IF EXISTS HAS_STOCK;
DROP TABLE IF EXISTS BATCH;
DROP TABLE IF EXISTS PRODUCT;
DROP TABLE IF EXISTS STORE;
DROP TABLE IF EXISTS SUPPLIER;
DROP TABLE IF EXISTS CATEGORY;
DROP TABLE IF EXISTS ADDRESS;
DROP TABLE IF EXISTS REPORT_EMAIL_LOG;
SET FOREIGN_KEY_CHECKS = 1;

-- TABLES
CREATE TABLE ADDRESS (
    address_id INT AUTO_INCREMENT PRIMARY KEY,
    street VARCHAR(200),
    city VARCHAR(100),
    country VARCHAR(100)
);

CREATE TABLE CATEGORY (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100)
);

CREATE TABLE SUPPLIER (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    address_id INT,
    FOREIGN KEY (address_id) REFERENCES ADDRESS(address_id)
);

CREATE TABLE STORE (
    store_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    address_id INT,
    FOREIGN KEY (address_id) REFERENCES ADDRESS(address_id)
);

CREATE TABLE PRODUCT (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    unit_price FLOAT,
    supplier_id INT,
    category_id INT,
    FOREIGN KEY (supplier_id) REFERENCES SUPPLIER(supplier_id),
    FOREIGN KEY (category_id) REFERENCES CATEGORY(category_id)
);

CREATE TABLE BATCH (
    batch_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    batch_code VARCHAR(50),
    expiration_date DATE,
    FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id)
);

CREATE TABLE HAS_STOCK (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT,
    batch_id INT,
    quantity INT,
    reorder_level INT DEFAULT 10,
    FOREIGN KEY (store_id) REFERENCES STORE(store_id),
    FOREIGN KEY (batch_id) REFERENCES BATCH(batch_id)
);

CREATE TABLE SALE (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount FLOAT,
    store_id INT,
    FOREIGN KEY (store_id) REFERENCES STORE(store_id)
);

CREATE TABLE SALE_LINE (
    line_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT,
    batch_id INT,
    quantity INT,
    subtotal FLOAT,
    FOREIGN KEY (sale_id) REFERENCES SALE(sale_id),
    FOREIGN KEY (batch_id) REFERENCES BATCH(batch_id)
);

CREATE TABLE REPLENISHMENT_FREQUENCY (
    frequency_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    store_id INT NOT NULL,
    replenishment_frequency INT NOT NULL,
    last_replenishment_date DATE,
    FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id),
    FOREIGN KEY (store_id) REFERENCES STORE(store_id),
    UNIQUE KEY uq_product_store (product_id, store_id),
    CHECK (replenishment_frequency >= 1 AND replenishment_frequency <= 3)
);

CREATE TABLE REPLENISHMENT_LIST (
    list_id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    list_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes VARCHAR(500),
    FOREIGN KEY (store_id) REFERENCES STORE(store_id)
);

CREATE TABLE REPLENISHMENT_LIST_ITEM (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    list_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    current_stock INT NOT NULL,
    reason VARCHAR(100) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    notes VARCHAR(500),
    FOREIGN KEY (list_id) REFERENCES REPLENISHMENT_LIST(list_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id)
);

CREATE TABLE REPLENISHMENT_LOG (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    store_id INT NOT NULL,
    batch_id INT NOT NULL,
    expiration_date DATE NOT NULL,
    quantity INT NOT NULL,
    user_id INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id),
    FOREIGN KEY (store_id) REFERENCES STORE(store_id),
    FOREIGN KEY (batch_id) REFERENCES BATCH(batch_id)
);

CREATE TABLE REPORT_EMAIL_LOG (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    store_id INT,
    year INT NOT NULL,
    month INT NOT NULL,
    recipients VARCHAR(500) NOT NULL,
    status VARCHAR(30) NOT NULL,
    message VARCHAR(1000),
    FOREIGN KEY (store_id) REFERENCES STORE(store_id)
);

-- SAMPLE DATA

-- Addresses
INSERT INTO ADDRESS (street, city, country) VALUES
('123 Main St', 'New York', 'USA'),
('456 Market St', 'London', 'UK'),
('789 Central Ave', 'Berlin', 'Germany');

-- Categories
INSERT INTO CATEGORY (category_name) VALUES
('Dairy'),
('Bakery'),
('Beverages');

-- Suppliers
INSERT INTO SUPPLIER (name, address_id) VALUES
('Best Foods Inc', 1),
('Bakery Supplies Co', 2),
('Drinks Ltd', 3);

-- Stores
INSERT INTO STORE (name, address_id) VALUES
('SuperMart Center', 2),
('Berlin Fresh', 3);

-- Products
INSERT INTO PRODUCT (name, unit_price, supplier_id, category_id) VALUES
('Yogurt Strawberry', 1.50, 1, 1),
('Milk 1L', 1.20, 1, 1),
('Bread Whole Grain', 2.50, 2, 2),
('Orange Juice', 3.00, 3, 3),
('Expired Yogurt', 1.00, 1, 1);

-- Batches
INSERT INTO BATCH (product_id, batch_code, expiration_date) VALUES
(1, 'BATCH-LOW-STOCK', '2030-12-31'),
(2, 'BATCH-OVERSTOCK', '2030-12-31'),
(3, 'BATCH-NORMAL', '2030-12-31'),
(4, 'BATCH-FRESH', '2030-12-31'),
(5, 'BATCH-DANGER', DATE_ADD(CURRENT_DATE, INTERVAL 1 DAY));

-- Stock Scenarios
INSERT INTO HAS_STOCK (store_id, batch_id, quantity, reorder_level) VALUES
-- Low stock
(1, 1, 5, 10),
-- Overstock
(1, 2, 500, 20),
-- Normal stock
(1, 3, 50, 20),
-- Normal stock
(1, 4, 100, 30),
-- Expiring tomorrow
(1, 5, 15, 5),
-- Berlin Fresh store
(2, 1, 20, 10),
(2, 3, 10, 10);

-- Replenishment Frequencies
INSERT INTO REPLENISHMENT_FREQUENCY (product_id, store_id, replenishment_frequency) VALUES
(1, 1, 1),
(2, 1, 2),
(5, 1, 3),
(1, 2, 2),
(3, 2, 1);

-- Sales
INSERT INTO SALE (store_id, total_amount) VALUES
(1, 10.50),
(1, 15.00),
(2, 8.00);

-- Sale lines
INSERT INTO SALE_LINE (sale_id, batch_id, quantity, subtotal) VALUES
(1, 1, 3, 4.50),
(1, 2, 2, 6.00),
(2, 3, 4, 10.00),
(2, 4, 1, 5.00),
(3, 1, 2, 3.00);

-- Replenishment Lists
INSERT INTO REPLENISHMENT_LIST (store_id, list_date, status, notes) VALUES
(1, CURRENT_DATE, 'draft', 'Weekly replenishment'),
(2, CURRENT_DATE, 'completed', 'Berlin replenishment');

-- Replenishment List Items
INSERT INTO REPLENISHMENT_LIST_ITEM (list_id, product_id, quantity, current_stock, reason, priority, notes) VALUES
(1, 1, 20, 5, 'Low stock', 'High', 'Urgent'),
(1, 2, 50, 500, 'Overstock', 'Low', 'Check storage'),
(2, 1, 15, 20, 'Weekly replenishment', 'Medium', NULL),
(2, 3, 5, 10, 'Normal stock', 'Low', 'Check bakery');

-- Replenishment Logs
INSERT INTO REPLENISHMENT_LOG (product_id, store_id, batch_id, expiration_date, quantity, user_id) VALUES
(1, 1, 1, '2030-12-31', 20, 1),
(2, 1, 2, '2030-12-31', 50, 1),
(3, 2, 3, '2030-12-31', 5, 2);

-- Report Email Logs
INSERT INTO REPORT_EMAIL_LOG (store_id, year, month, recipients, status, message) VALUES
(1, 2026, 1, 'manager@supermart.com', 'sent', 'Monthly stock report'),
(2, 2026, 1, 'berlin@fresh.com', 'pending', 'Weekly replenishment report');
