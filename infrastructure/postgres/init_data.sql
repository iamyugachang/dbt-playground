-- Create databases
CREATE DATABASE metastore;
CREATE DATABASE shop;

-- Connect to shop and create initial data
\c shop;

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    signup_date DATE
);

INSERT INTO customers (name, email, signup_date) VALUES
('Alice', 'alice@example.com', '2023-01-01'),
('Bob', 'bob@example.com', '2023-02-15'),
('Charlie', 'charlie@example.com', '2023-03-10');

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2)
);

INSERT INTO products (name, price) VALUES
('Laptop', 999.99),
('Mouse', 29.99),
('Keyboard', 59.99);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER,
    order_date DATE
);

INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES
(1, 1, 1, '2023-01-05'),
(1, 3, 2, '2023-02-10'),
(2, 2, 1, '2023-02-20'),
(3, 1, 1, '2023-03-15'),
(3, 2, 3, '2023-04-01'),
(2, 3, 1, '2023-04-12');
