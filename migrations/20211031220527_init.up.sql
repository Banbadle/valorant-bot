BEGIN;

CREATE TABLE IF NOT EXISTS users (
  id BIGINT NOT NULL, -- Discord user id
  username VARCHAR(255) NOT NULL, -- Discord username
  tag SMALLINT(255) NOT NULL, -- Discord tag
  social_credit INT NOT NULL DEFAULT 0,
  val_username VARCHAR(255), -- Valorant username
  val_tag VARCHAR(255), -- Valorant tag
  -- on time and not on time
  created TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (id),
  UNIQUE (username, tag),
  UNIQUE (val_username, val_tag)
);

CREATE TABLE IF NOT EXISTS messages (
  id BIGINT NOT NULL, -- Discord message id
  guild_id BIGINT NOT NULL, -- Discord guild id
  channel_id BIGINT NOT NULL, -- Discord channel id
  created_by BIGINT NOT NULL, -- Discord user id
  created TIMESTAMP NOT NULL DEFAULT NOW(),
  FOREIGN KEY (created_by) REFERENCES users(id),
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS reactions (
  id INT NOT NULL AUTO_INCREMENT,
  message_id BIGINT NOT NULL, -- Discord message id
  user_id BIGINT NOT NULL, -- Discord user id
  emoji CHAR(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT NOW(),
  removed TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE (message_id, user_id, emoji),
  FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

COMMIT;
