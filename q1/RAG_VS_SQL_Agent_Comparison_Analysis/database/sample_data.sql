-- ============================================================================
-- E-COMMERCE SAMPLE DATA
-- ============================================================================
-- This file populates the database with realistic test data for the SQL agent
-- to work with. Includes customers, products, orders, reviews, and support tickets.
-- ============================================================================

-- Clear existing data (in correct order due to foreign key constraints)
DELETE FROM support_tickets;
DELETE FROM reviews;
DELETE FROM orders;
DELETE FROM products;
DELETE FROM customers;

-- Reset sequences to start from 1
ALTER SEQUENCE customers_customer_id_seq RESTART WITH 1;
ALTER SEQUENCE products_product_id_seq RESTART WITH 1;
ALTER SEQUENCE orders_order_id_seq RESTART WITH 1;
ALTER SEQUENCE reviews_review_id_seq RESTART WITH 1;
ALTER SEQUENCE support_tickets_ticket_id_seq RESTART WITH 1;

-- ============================================================================
-- SAMPLE CUSTOMERS DATA
-- ============================================================================
-- Insert realistic customer data with various demographics
INSERT INTO customers (name, email, phone, address) VALUES
('John Doe', 'john.doe@email.com', '+1-555-0101', '123 Main Street, Springfield, IL 62701'),
('Jane Smith', 'jane.smith@gmail.com', '+1-555-0102', '456 Oak Avenue, Chicago, IL 60601'),
('Mike Johnson', 'mike.johnson@yahoo.com', '+1-555-0103', '789 Pine Road, Aurora, IL 60502'),
('Sarah Wilson', 'sarah.wilson@outlook.com', '+1-555-0104', '321 Elm Street, Rockford, IL 61101'),
('David Brown', 'david.brown@email.com', '+1-555-0105', '654 Maple Drive, Peoria, IL 61602'),
('Lisa Davis', 'lisa.davis@gmail.com', '+1-555-0106', '987 Cedar Lane, Decatur, IL 62521'),
('Tom Miller', 'tom.miller@yahoo.com', '+1-555-0107', '147 Birch Boulevard, Champaign, IL 61820'),
('Amy Taylor', 'amy.taylor@outlook.com', '+1-555-0108', '258 Walnut Way, Evanston, IL 60201'),
('Chris Anderson', 'chris.anderson@email.com', '+1-555-0109', '369 Hickory Hill, Naperville, IL 60540'),
('Emma Martinez', 'emma.martinez@gmail.com', '+1-555-0110', '741 Ash Avenue, Joliet, IL 60431');

-- ============================================================================
-- SAMPLE PRODUCTS DATA
-- ============================================================================
-- Insert various product categories with different price ranges
INSERT INTO products (name, category, price, stock_quantity, description) VALUES
-- Electronics
('Wireless Bluetooth Mouse', 'Electronics', 29.99, 50, 'Ergonomic wireless mouse with long battery life'),
('Noise-Cancelling Headphones', 'Electronics', 149.99, 25, 'Premium headphones with active noise cancellation'),
('USB-C Charging Cable', 'Electronics', 12.99, 100, '6-foot braided USB-C to USB-A cable'),
('Portable Phone Charger', 'Electronics', 39.99, 35, '10000mAh power bank with fast charging'),
('Bluetooth Speaker', 'Electronics', 79.99, 20, 'Waterproof portable speaker with rich sound'),

-- Home & Kitchen
('Ceramic Coffee Mug', 'Home & Kitchen', 14.99, 75, '12oz ceramic mug with comfortable handle'),
('Stainless Steel Water Bottle', 'Home & Kitchen', 24.99, 60, '32oz insulated water bottle keeps drinks cold'),
('Non-Stick Frying Pan', 'Home & Kitchen', 49.99, 30, '10-inch non-stick pan with heat-resistant handle'),
('Kitchen Knife Set', 'Home & Kitchen', 89.99, 15, '5-piece professional knife set with wooden block'),
('Electric Kettle', 'Home & Kitchen', 34.99, 25, '1.7L electric kettle with auto shut-off'),

-- Office Supplies
('Adjustable Laptop Stand', 'Office Supplies', 45.99, 40, 'Aluminum laptop stand with 6 height adjustments'),
('Wireless Keyboard', 'Office Supplies', 69.99, 20, 'Compact wireless keyboard with backlight'),
('Desk Organizer', 'Office Supplies', 19.99, 50, 'Bamboo desk organizer with multiple compartments'),
('Ergonomic Office Chair', 'Office Supplies', 299.99, 10, 'Mesh office chair with lumbar support'),
('LED Desk Lamp', 'Office Supplies', 39.99, 30, 'Adjustable LED lamp with USB charging port'),

-- Accessories
('Phone Case - iPhone', 'Accessories', 19.99, 80, 'Clear protective case with reinforced corners'),
('Sunglasses', 'Accessories', 59.99, 45, 'UV protection sunglasses with polarized lenses'),
('Leather Wallet', 'Accessories', 39.99, 35, 'Genuine leather bifold wallet with RFID blocking'),
('Fitness Tracker', 'Accessories', 99.99, 25, 'Water-resistant fitness tracker with heart rate monitor'),
('Baseball Cap', 'Accessories', 24.99, 55, 'Adjustable cotton baseball cap in multiple colors');

-- ============================================================================
-- SAMPLE ORDERS DATA
-- ============================================================================
-- Insert orders with various statuses and amounts
INSERT INTO orders (customer_id, order_date, status, total_amount) VALUES
-- Recent orders
(1, '2025-07-18 10:30:00', 'pending', 79.98),
(2, '2025-07-18 14:15:00', 'confirmed', 149.99),
(3, '2025-07-17 09:45:00', 'shipped', 94.98),
(4, '2025-07-17 16:20:00', 'delivered', 29.99),
(5, '2025-07-16 11:10:00', 'delivered', 154.97),

-- Older orders
(6, '2025-07-15 13:30:00', 'delivered', 69.99),
(7, '2025-07-14 08:45:00', 'delivered', 34.99),
(1, '2025-07-13 15:20:00', 'delivered', 45.99),
(8, '2025-07-12 10:15:00', 'cancelled', 299.99),
(9, '2025-07-11 12:40:00', 'delivered', 59.99),

-- Even older orders for history
(10, '2025-07-10 14:25:00', 'delivered', 89.99),
(2, '2025-07-09 09:30:00', 'delivered', 19.99),
(3, '2025-07-08 16:45:00', 'delivered', 24.99),
(4, '2025-07-07 11:20:00', 'delivered', 39.99),
(5, '2025-07-06 13:15:00', 'delivered', 99.99);

-- ============================================================================
-- SAMPLE REVIEWS DATA
-- ============================================================================
-- Insert product reviews with various ratings and comments
INSERT INTO reviews (customer_id, product_id, rating, comment) VALUES
-- Wireless Mouse reviews
(1, 1, 5, 'Excellent mouse! Very responsive and comfortable to use.'),
(4, 1, 4, 'Good mouse overall, battery life is great as advertised.'),
(7, 1, 5, 'Perfect for work. No lag and fits my hand perfectly.'),

-- Headphones reviews
(2, 2, 5, 'Amazing noise cancellation! Perfect for flights and commuting.'),
(6, 2, 4, 'Great sound quality but a bit heavy for long use.'),

-- Coffee Mug reviews
(5, 6, 5, 'Perfect size for my morning coffee. Great quality ceramic.'),
(10, 6, 4, 'Nice mug, comfortable handle but wish it kept coffee warmer longer.'),

-- Phone Case reviews
(4, 16, 3, 'Decent protection but yellowed after a few months.'),
(8, 16, 4, 'Good clear case, easy to install and remove.'),

-- Laptop Stand reviews
(1, 11, 5, 'Excellent build quality! Really improved my posture while working.'),
(3, 11, 4, 'Sturdy and adjustable, good value for money.'),

-- Water Bottle reviews
(9, 7, 5, 'Keeps drinks cold all day! Love the design.'),
(6, 7, 5, 'Best water bottle I ever owned. No leaks and perfect size.'),

-- Fitness Tracker reviews
(5, 18, 4, 'Accurate heart rate monitoring and good battery life.'),
(9, 18, 3, 'Good features but the band broke after 6 months.'),

-- Bluetooth Speaker reviews
(10, 5, 4, 'Great sound for the size. Waterproof feature works well.'),

-- Sunglasses reviews
(8, 17, 5, 'Stylish and great UV protection. Very comfortable.');

-- ============================================================================
-- SAMPLE SUPPORT TICKETS DATA
-- ============================================================================
-- Insert support tickets with various statuses and priorities
INSERT INTO support_tickets (customer_id, subject, description, status, priority) VALUES
-- Open tickets (recent issues)
(1, 'Order not received', 'I placed order #1 three days ago but have not received shipping confirmation. Can you please check the status?', 'open', 'high'),
(3, 'Product defect - Bluetooth Mouse', 'The wireless mouse I received yesterday is not connecting properly to my computer. Left click seems to be faulty.', 'open', 'medium'),
(8, 'Billing question', 'I see an extra charge of $5.99 on my last order but cannot figure out what it is for. Please explain.', 'open', 'low'),
(2, 'Cannot login to account', 'I forgot my password and the reset link is not working. Please help me regain access to my account.', 'open', 'medium'),

-- In progress tickets
(5, 'Refund request for cancelled order', 'Order #9 was cancelled but I have not received my refund yet. It has been a week since cancellation.', 'in_progress', 'high'),
(6, 'Wrong item delivered', 'I ordered a phone case but received sunglasses instead. Need to exchange for correct item.', 'in_progress', 'medium'),

-- Resolved tickets (examples of completed support)
(4, 'Shipping delay inquiry', 'My order was supposed to arrive yesterday but tracking shows it is still in transit.', 'resolved', 'low'),
(7, 'Product recommendation request', 'Looking for a good wireless keyboard under $100 for my home office setup.', 'resolved', 'low'),
(9, 'Account information update', 'Need to update my shipping address for future orders.', 'resolved', 'low'),
(10, 'Warranty claim for headphones', 'My noise-cancelling headphones stopped working after 3 months. Want to claim warranty.', 'resolved', 'medium'),

-- Closed tickets
(1, 'Thank you for excellent service', 'Just wanted to thank the support team for quick resolution of my previous issue.', 'closed', 'low'),
(2, 'Product inquiry about laptop stand', 'Asked about compatibility with MacBook Pro 16 inch.', 'closed', 'low');

-- ============================================================================
-- DATA VERIFICATION AND SUCCESS MESSAGE
-- ============================================================================
DO $$
DECLARE
    customer_count INTEGER;
    product_count INTEGER;
    order_count INTEGER;
    review_count INTEGER;
    ticket_count INTEGER;
BEGIN
    -- Count records in each table
    SELECT COUNT(*) INTO customer_count FROM customers;
    SELECT COUNT(*) INTO product_count FROM products;
    SELECT COUNT(*) INTO order_count FROM orders;
    SELECT COUNT(*) INTO review_count FROM reviews;
    SELECT COUNT(*) INTO ticket_count FROM support_tickets;
    
    -- Display success message with counts
    RAISE NOTICE '================================================================';
    RAISE NOTICE '✅ SAMPLE DATA INSERTED SUCCESSFULLY!';
    RAISE NOTICE '================================================================';
    RAISE NOTICE 'Data Summary:';
    RAISE NOTICE '  📋 Customers: % records', customer_count;
    RAISE NOTICE '  📦 Products: % records', product_count;
    RAISE NOTICE '  🛒 Orders: % records', order_count;
    RAISE NOTICE '  ⭐ Reviews: % records', review_count;
    RAISE NOTICE '  🎫 Support Tickets: % records', ticket_count;
    RAISE NOTICE '================================================================';
    RAISE NOTICE '🚀 Database is ready for SQL Agent testing!';
    RAISE NOTICE '================================================================';
    RAISE NOTICE 'Sample queries you can test:';
    RAISE NOTICE '  • "Show all orders for John Doe"';
    RAISE NOTICE '  • "List all pending support tickets"';
    RAISE NOTICE '  • "Find reviews for Wireless Bluetooth Mouse"';
    RAISE NOTICE '  • "Show customers with high priority tickets"';
    RAISE NOTICE '  • "List products in Electronics category"';
    RAISE NOTICE '================================================================';
END $$;
