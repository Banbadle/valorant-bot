ALTER TABLE users ALTER COLUMN social_credit SET DEFAULT 100;
UPDATE users
SET social_credit = 100;