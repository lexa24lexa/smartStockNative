CREATE DATABASE IF NOT EXISTS retail_bd;
USE retail_bd;

-- Clean
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS SALE_LINE;
DROP TABLE IF EXISTS SALE;
DROP TABLE IF EXISTS HAS_STOCK;
DROP TABLE IF EXISTS BATCH;
DROP TABLE IF EXISTS PRODUCT;
DROP TABLE IF EXISTS STORE;
DROP TABLE IF EXISTS SUPPLIER;
DROP TABLE IF EXISTS CATEGORY;
DROP TABLE IF EXISTS ADDRESS;
SET FOREIGN_KEY_CHECKS = 1;

-- Table creation
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
    reorder_level INT DEFAULT 10, -- FR02: Minimum stock level column
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

-- Dummy Data

INSERT INTO ADDRESS (address_id, street, city, country) VALUES 
(1, '123 Main St', 'New York', 'USA'),
(2, '456 Market St', 'London', 'UK');

INSERT INTO CATEGORY (category_id, category_name) VALUES (100, 'Dairy');
INSERT INTO SUPPLIER (supplier_id, name, address_id) VALUES (100, 'Best Foods Inc', 1);

INSERT INTO STORE (store_id, name, address_id) VALUES (100, 'SuperMart Center', 2);

INSERT INTO PRODUCT (product_id, name, unit_price, supplier_id, category_id) VALUES 
(100, 'Yogurt Strawberry', 1.50, 100, 100),
(101, 'Milk 1L', 1.20, 100, 100),
(999, 'Expired Yogurt', 1.00, 100, 100);

INSERT INTO BATCH (batch_id, product_id, batch_code, expiration_date) VALUES 
(100, 100, 'BATCH-LOW-STOCK', '2030-12-31'),
(101, 101, 'BATCH-OVERSTOCK', '2030-12-31'),
(999, 999, 'BATCH-DANGER', DATE_ADD(CURRENT_DATE, INTERVAL 1 DAY));

-- SCENARIOS FOR ALERTS:
-- 1. Low Stock (FR02/FR17): Qty (5) <= Reorder Level (10)
INSERT INTO HAS_STOCK (store_id, batch_id, quantity, reorder_level) VALUES (100, 100, 5, 10);

-- 2. Overstock (FR17 Custom Rule): Qty (500) > 3 * Reorder Level (20) -> 500 > 60
INSERT INTO HAS_STOCK (store_id, batch_id, quantity, reorder_level) VALUES (100, 101, 500, 20);

-- 3. Expiring (FR17): Expires tomorrow
INSERT INTO HAS_STOCK (store_id, batch_id, quantity, reorder_level) VALUES (100, 999, 15, 5);