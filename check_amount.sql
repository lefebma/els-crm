-- Check if amount column exists
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'opportunities' AND column_name = 'amount';

-- Add amount column if it doesn't exist
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS amount NUMERIC(15, 2);

-- Verify the column was added
SELECT column_name, data_type, numeric_precision, numeric_scale
FROM information_schema.columns 
WHERE table_name = 'opportunities' AND column_name = 'amount'; 