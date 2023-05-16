ALTER TABLE users ALTER COLUMN social_credit SET DEFAULT 0;
UPDATE users
SET social_credit = 0;