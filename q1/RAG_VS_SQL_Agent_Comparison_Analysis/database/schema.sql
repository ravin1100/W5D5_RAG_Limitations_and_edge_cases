-- ============================================================================
-- E-COMMERCE DATABASE SCHEMA (SIMPLIFIED VERSION)
-- ============================================================================
-- This creates the core tables needed for the SQL agent system:
-- customers, products, orders, reviews, and support_tickets
-- ============================================================================

-- Clean up existing tables
DROP TABLE IF EXISTS support_tickets CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- ============================================================================
-- CUSTOMERS TABLE - Store customer information
-- ============================================================================
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,        -- Unique customer ID
    name VARCHAR(100) NOT NULL,            -- Customer full name
    email VARCHAR(150) UNIQUE NOT NULL,    -- Email (must be unique)
    phone VARCHAR(20),                     -- Phone number
    address TEXT,                          -- Customer address
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster searches
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_name ON customers(name);

-- ============================================================================
-- PRODUCTS TABLE - Store product catalog
-- ============================================================================
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,         -- Unique product ID
    name VARCHAR(200) NOT NULL,            -- Product name
    category VARCHAR(100) NOT NULL,        -- Product category
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),  -- Price (non-negative)
    stock_quantity INTEGER DEFAULT 0,      -- Available stock
    description TEXT,                      -- Product description
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for product searches
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_name ON products(name);

-- ============================================================================
-- ORDERS TABLE - Store customer orders
-- ============================================================================
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,           -- Unique order ID
    customer_id INTEGER NOT NULL,          -- Link to customer
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',  -- Order status
    total_amount DECIMAL(10,2) NOT NULL,   -- Order total
    
    -- Link to customer table
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) 
        REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- Indexes for order queries
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_date ON orders(order_date);

-- ============================================================================
-- REVIEWS TABLE - Store product reviews
-- ============================================================================
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,          -- Unique review ID
    customer_id INTEGER NOT NULL,          -- Who wrote the review
    product_id INTEGER NOT NULL,           -- Which product
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5), -- 1-5 stars
    comment TEXT,                          -- Review text
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Links to other tables
    CONSTRAINT fk_reviews_customer FOREIGN KEY (customer_id) 
        REFERENCES customers(customer_id) ON DELETE CASCADE,
    CONSTRAINT fk_reviews_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) ON DELETE CASCADE
);

-- Indexes for review queries
CREATE INDEX idx_reviews_customer_id ON reviews(customer_id);
CREATE INDEX idx_reviews_product_id ON reviews(product_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);

-- ============================================================================
-- SUPPORT_TICKETS TABLE - Store customer support requests
-- ============================================================================
CREATE TABLE support_tickets (
    ticket_id SERIAL PRIMARY KEY,          -- Unique ticket ID
    customer_id INTEGER NOT NULL,          -- Which customer
    subject VARCHAR(200) NOT NULL,         -- Brief issue description
    description TEXT NOT NULL,             -- Detailed problem description
    status VARCHAR(20) DEFAULT 'open',     -- Ticket status
    priority VARCHAR(10) DEFAULT 'medium', -- Priority level
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Link to customer
    CONSTRAINT fk_support_tickets_customer FOREIGN KEY (customer_id) 
        REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- Indexes for support ticket queries
CREATE INDEX idx_support_tickets_customer_id ON support_tickets(customer_id);
CREATE INDEX idx_support_tickets_status ON support_tickets(status);
CREATE INDEX idx_support_tickets_priority ON support_tickets(priority);

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '================================================================';
    RAISE NOTICE '✅ DATABASE SCHEMA CREATED SUCCESSFULLY!';
    RAISE NOTICE '================================================================';
    RAISE NOTICE 'Created tables: customers, products, orders, reviews, support_tickets';
    RAISE NOTICE 'All indexes and foreign keys are set up';
    RAISE NOTICE '🚀 Ready for sample data!';
    RAISE NOTICE '================================================================';
END $$;
