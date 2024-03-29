CREATE TABLE IF NOT EXISTS users (
  id BIGINT NOT NULL, -- Discord user id
  username VARCHAR(255) NOT NULL, -- Discord username
  tag SMALLINT(255) NOT NULL, -- Discord tag
  social_credit INT NOT NULL DEFAULT 100,
  val_username VARCHAR(255), -- Valorant username
  val_tag VARCHAR(255), -- Valorant tag
  val_rank TINYINT(8), -- Valorant rank
  notify TINYINT(1) NOT NULL DEFAULT 1, -- Notify on message updates
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

CREATE TABLE IF NOT EXISTS crediteventtypes (
  id INT NOT NULL AUTO_INCREMENT,
  event_name VARCHAR(255) NOT NULL,
  event_category VARCHAR(255) NOT NULL DEFAULT "Misc",
  default_value INT NOT NULL,
  cooldown INT NOT NULL DEFAULT 30,
  public BOOL NOT NULL DEFAULT TRUE,
  PRIMARY KEY (id),
  UNIQUE `unq_event_name` (event_name);
);

CREATE TABLE IF NOT EXISTS creditchanges (
  id INT NOT NULL AUTO_INCREMENT,
  user_id BIGINT NOT NULL, -- Discord user id
  event_name VARCHAR(255) NOT NULL,
  change_value BIGINT NOT NULL,
  start_time TIMESTAMP NOT NULL DEFAULT UTC_TIMESTAMP(),
  vote_msg_id BIGINT, -- Discord message id
  cause_user_id BIGINT DEFAULT NULL, -- Discord user id
  processed BOOL DEFAULT 1,
  end_time TIMESTAMP NOT NULL DEFAULT UTC_TIMESTAMP(),  -- alt: ADDTIME(UTC_TIMESTAMP(), "0:30:0"),
  verdict_msg_id BIGINT, -- Discord message id
  PRIMARY KEY (id),
  FOREIGN KEY `fk_creditchanges_user_id` (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS creditvotes (
  id INT NOT NULL AUTO_INCREMENT,
  message_id BIGINT NOT NULL, -- Discord message id
  user_id BIGINT NOT NULL, -- Discord user id
  vote BOOL NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT UTC_TIMESTAMP(),
  PRIMARY KEY (id),
  UNIQUE `message_user_time` (message_id, user_id)
);
