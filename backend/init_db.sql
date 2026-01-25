CREATE DATABASE IF NOT EXISTS retail_bd;
USE retail_bd;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS STOCK_MOVEMENT;
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
DROP TABLE IF EXISTS USER;
DROP TABLE IF EXISTS USER_ROLE;

SET FOREIGN_KEY_CHECKS = 1;

-- Tables creation

-- Address table
CREATE TABLE ADDRESS (
    address_id INT AUTO_INCREMENT PRIMARY KEY,
    street VARCHAR(200),
    city VARCHAR(100),
    country VARCHAR(100)
);

-- Product categories
CREATE TABLE CATEGORY (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

-- Suppliers
CREATE TABLE SUPPLIER (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address_id INT,
    FOREIGN KEY (address_id) REFERENCES ADDRESS(address_id)
);

-- Stores
CREATE TABLE STORE (
    store_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address_id INT,
    FOREIGN KEY (address_id) REFERENCES ADDRESS(address_id)
);

-- Products with supplier and category
CREATE TABLE PRODUCT (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    unit_price FLOAT NOT NULL CHECK(unit_price >= 0),
    supplier_id INT NOT NULL,
    category_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (supplier_id) REFERENCES SUPPLIER(supplier_id),
    FOREIGN KEY (category_id) REFERENCES CATEGORY(category_id)
);

-- Product batches
CREATE TABLE BATCH (
    batch_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    batch_code VARCHAR(50) NOT NULL,
    expiration_date DATE,
    UNIQUE KEY uq_product_batch_code (product_id, batch_code),
    FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id)
);

-- Stock per store
CREATE TABLE HAS_STOCK (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    batch_id INT NOT NULL,
    quantity INT NOT NULL CHECK(quantity >= 0),
    reorder_level INT NOT NULL DEFAULT 10 CHECK(reorder_level >= 0),
    UNIQUE KEY uq_store_batch_stock (store_id, batch_id),
    FOREIGN KEY (store_id) REFERENCES STORE(store_id),
    FOREIGN KEY (batch_id) REFERENCES BATCH(batch_id)
);

-- Sales
CREATE TABLE SALE (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount FLOAT,
    store_id INT,
    FOREIGN KEY (store_id) REFERENCES STORE(store_id)
);

-- Sale lines
CREATE TABLE SALE_LINE (
    line_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT,
    batch_id INT,
    quantity INT,
    subtotal FLOAT,
    FOREIGN KEY (sale_id) REFERENCES SALE(sale_id),
    FOREIGN KEY (batch_id) REFERENCES BATCH(batch_id)
);

-- Replenishment frequency per product/store
CREATE TABLE REPLENISHMENT_FREQUENCY (
    frequency_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    store_id INT NOT NULL,
    replenishment_frequency INT NOT NULL CHECK(replenishment_frequency BETWEEN 1 AND 3),
    last_replenishment_date DATE,
    UNIQUE KEY uq_product_store (product_id, store_id),
    FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id),
    FOREIGN KEY (store_id) REFERENCES STORE(store_id)
);

-- Replenishment lists
CREATE TABLE REPLENISHMENT_LIST (
    list_id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    list_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes VARCHAR(500),
    FOREIGN KEY (store_id) REFERENCES STORE(store_id)
);

-- Items in replenishment lists
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

-- Replenishment logs
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

-- Report email logs
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

-- User roles
CREATE TABLE USER_ROLE (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

-- Users
CREATE TABLE USER (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    store_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (role_id) REFERENCES USER_ROLE(role_id),
    FOREIGN KEY (store_id) REFERENCES STORE(store_id)
);

-- Stock movements
CREATE TABLE STOCK_MOVEMENT (
    movement_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    batch_id INT NOT NULL,
    quantity INT NOT NULL,
    origin_type VARCHAR(50) NOT NULL,
    origin_id INT,
    destination_type VARCHAR(50) NOT NULL,
    destination_id INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id),
    FOREIGN KEY (batch_id) REFERENCES BATCH(batch_id)
);

-- Sample data

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
INSERT INTO PRODUCT (name, unit_price, supplier_id, category_id, is_active) VALUES
('Yogurt Strawberry', 1.50, 1, 1, TRUE),
('Milk 1L', 1.20, 1, 1, TRUE),
('Bread Whole Grain', 2.50, 2, 2, TRUE),
('Orange Juice', 3.00, 3, 3, TRUE),
('Soja Milk', 1.00, 1, 1, TRUE);

-- Batches
INSERT INTO BATCH (product_id, batch_code, expiration_date) VALUES
(1, 'BATCH-LOW-STOCK', '2030-12-31'),
(2, 'BATCH-OVERSTOCK', '2030-12-31'),
(3, 'BATCH-NORMAL', '2030-12-31'),
(4, 'BATCH-FRESH', '2030-12-31'),
(5, 'BATCH-DANGER', '2030-12-31');

-- Stock
INSERT INTO HAS_STOCK (store_id, batch_id, quantity, reorder_level) VALUES
(1, 1, 5, 10),
(1, 2, 500, 20),
(1, 3, 50, 20),
(1, 4, 100, 30),
(1, 5, 15, 5),
(2, 1, 20, 10),
(2, 3, 10, 10);

-- Stock movements
INSERT INTO STOCK_MOVEMENT (product_id, batch_id, quantity, origin_type, origin_id, destination_type, destination_id, timestamp) VALUES
-- Movements to store 1
(1, 1, 5, 'SUPPLIER', 1, 'STORE', 1, '2026-01-01 09:00:00'),
(2, 2, 50, 'SUPPLIER', 1, 'STORE', 1, '2026-01-02 10:00:00'),
(3, 3, 10, 'SUPPLIER', 2, 'STORE', 2, '2026-01-03 11:00:00'),
(4, 4, 100, 'SUPPLIER', 3, 'STORE', 1, '2026-01-04 12:00:00'),
(5, 5, 15, 'SUPPLIER', 1, 'STORE', 1, '2026-01-05 13:00:00'),

-- Internal transfers between stores
(1, 1, 10, 'STORE', 2, 'STORE', 1, '2026-01-06 14:00:00'),
(3, 3, 5, 'STORE', 1, 'STORE', 2, '2026-01-07 15:00:00');

-- Replenishment frequency
INSERT INTO REPLENISHMENT_FREQUENCY (product_id, store_id, replenishment_frequency, last_replenishment_date) VALUES
(1, 1, 1, NULL),
(2, 1, 2, NULL),
(5, 1, 3, NULL),
(1, 2, 2, NULL),
(3, 2, 1, NULL);

-- Sales (com datas em Janeiro 2026)
INSERT INTO SALE (store_id, total_amount, date) VALUES
(1, 10.50, '2026-01-05 10:30:00'),
(1, 15.00, '2026-01-10 14:15:00'),
(2, 8.00, '2026-01-12 09:00:00');

-- Sale lines
INSERT INTO SALE_LINE (sale_id, batch_id, quantity, subtotal) VALUES
(1, 1, 3, 4.50),
(1, 2, 2, 6.00),
(2, 3, 4, 10.00),
(2, 4, 1, 5.00),
(3, 1, 2, 3.00);

-- Replenishment lists
INSERT INTO REPLENISHMENT_LIST (store_id, list_date, status, notes) VALUES
(1, '2026-01-07', 'draft', 'Weekly replenishment'),
(2, '2026-01-08', 'completed', 'Berlin replenishment');

-- Replenishment list items
INSERT INTO REPLENISHMENT_LIST_ITEM (list_id, product_id, quantity, current_stock, reason, priority, notes) VALUES
(1, 1, 20, 5, 'Low stock', 'High', 'Urgent'),
(1, 2, 50, 500, 'Overstock', 'Low', 'Check storage'),
(2, 1, 15, 20, 'Weekly replenishment', 'Medium', NULL),
(2, 3, 5, 10, 'Normal stock', 'Low', 'Check bakery');

-- Replenishment logs
INSERT INTO REPLENISHMENT_LOG (product_id, store_id, batch_id, expiration_date, quantity, user_id) VALUES
(1, 1, 1, '2030-12-31', 20, 1),
(2, 1, 2, '2030-12-31', 50, 1),
(3, 2, 3, '2030-12-31', 5, 2);

-- Report email logs
INSERT INTO REPORT_EMAIL_LOG (store_id, year, month, recipients, status, message) VALUES
(1, 2026, 1, 'manager@supermart.com', 'sent', 'Monthly stock report'),
(2, 2026, 1, 'berlin@fresh.com', 'pending', 'Weekly replenishment report');

-- User roles
INSERT INTO USER_ROLE (role_name) VALUES
('employee'),
('manager');

-- Users
INSERT INTO USER (username, email, password_hash, role_id, store_id, is_active) VALUES
('john_employee', 'john@supermart.com', 'HASHED_PASSWORD_EMPLOYEE', 1, 1, 1),
('anna_manager', 'anna@berlinfresh.com', 'HASHED_PASSWORD_MANAGER', 2, 2, 1);