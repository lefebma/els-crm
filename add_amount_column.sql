-- SQL script to add amount column to opportunities table
-- Run this in Azure Portal > PostgreSQL Flexible Server > Query Editor

-- Check if the column already exists
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'opportunities' AND column_name = 'amount';

-- If no results returned, run this to add the column:
ALTER TABLE opportunities 
ADD COLUMN amount NUMERIC(15, 2);

-- Verify the column was added
SELECT column_name, data_type, numeric_precision, numeric_scale
FROM information_schema.columns 
WHERE table_name = 'opportunities' AND column_name = 'amount'; 