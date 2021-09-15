ALTER TABLE users
ADD val_username VARCHAR(255),
ADD val_tag VARCHAR(255),
ADD UNIQUE (val_username, val_tag),
DROP INDEX mention_id_2;