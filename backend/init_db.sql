CREATE DATABASE IF NOT EXISTS retail_bd;
USE retail_bd;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS REPLENISHMENT_LIST_ITEM;
DROP TABLE IF EXISTS REPLENISHMENT_LIST;
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
SET FOREIGN_KEY_CHECKS = 1;

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

-- Stock scenarios for testing alerts
-- 1. Low Stock (FR02): Qty (5) <= Reorder Level (10)
INSERT INTO HAS_STOCK (store_id, batch_id, quantity, reorder_level) VALUES (100, 100, 5, 10);

-- 2. Overstock (FR17 Custom Rule): Qty (500) > 3 * Reorder Level (20)
INSERT INTO HAS_STOCK (store_id, batch_id, quantity, reorder_level) VALUES (100, 101, 500, 20);

-- 3. Expiring (FR17): Expires tomorrow
INSERT INTO HAS_STOCK (store_id, batch_id, quantity, reorder_level) VALUES (100, 999, 15, 5);

-- Sample Replenishment Frequencies
-- Format: product_id, store_id, replenishment_frequency (days: 1-3)
INSERT INTO REPLENISHMENT_FREQUENCY (product_id, store_id, replenishment_frequency) VALUES 
(100, 100, 1),  -- Yogurt Strawberry: replenished daily
(999, 100, 3);  -- Expired Yogurt: replenished every 3 days
