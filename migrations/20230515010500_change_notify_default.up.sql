ALTER TABLE users ALTER COLUMN notify SET DEFAULT 1;
UPDATE users
SET notify = 1;