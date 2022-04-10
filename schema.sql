CREATE TABLE IF NOT EXISTS users (
  id BIGINT NOT NULL, -- Discord user id
  username VARCHAR(255) NOT NULL, -- Discord username
  tag SMALLINT(255) NOT NULL, -- Discord tag
  social_credit INT NOT NULL DEFAULT 0,
  val_username VARCHAR(255), -- Valorant username
  val_tag VARCHAR(255), -- Valorant tag
  val_rank TINYINT(8), -- Valorant rank
  notify TINYINT(1) NOT NULL DEFAULT 0, -- Notify on message updates
  is_admin TINYINT(1) NOT NULL DEFAULT 0,
  timezone VARCHAR(255) DEFAULT 'Europe/London',
  -- on time and not on time
  created TIMESTAMP NOT NULL DEFAULT UTC_TIMESTAMP(),
  PRIMARY KEY (id),
  UNIQUE `discord_user` (username, tag),
  UNIQUE `valorant_user` (val_username, val_tag)
);

CREATE TABLE IF NOT EXISTS messages (
  id BIGINT NOT NULL, -- Discord message id
  guild_id BIGINT NOT NULL, -- Discord guild id
  channel_id BIGINT NOT NULL, -- Discord channel id
  created_by BIGINT NOT NULL, -- Discord user id
  trigger_msg BIGINT NOT NULL, -- Discord message id which triggered this message
  created TIMESTAMP NOT NULL DEFAULT UTC_TIMESTAMP(),
  message_type TINYINT(8) NOT NULL DEFAULT 1,
  FOREIGN KEY `fk_created_by` (created_by) REFERENCES users(id),
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS reactions (
  id INT NOT NULL AUTO_INCREMENT,
  message_id BIGINT NOT NULL, -- Discord message id
  user_id BIGINT NOT NULL, -- Discord user id
  react_stamp BIGINT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT UTC_TIMESTAMP(),
  removed TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE `message_user_time` (message_id, user_id, react_stamp),
  FOREIGN KEY `fk_message_id` (message_id) REFERENCES messages(id) ON DELETE CASCADE,
  FOREIGN KEY `fk_reactions_user_id` (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS voicechannellog (
  id INT NOT NULL AUTO_INCREMENT,
  user_id BIGINT NOT NULL, -- Discord user id
  guild_id BIGINT NOT NULL, -- Discord guild id
  channel_id BIGINT NOT NULL, -- Discord channel id
  join_time TIMESTAMP NOT NULL DEFAULT UTC_TIMESTAMP(),
  leave_time TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY `fk_voice_user_id` (user_id) REFERENCES users(id) ON DELETE CASCADE
);
