CREATE TABLE IF NOT EXISTS voicechannellog (
  id INT NOT NULL AUTO_INCREMENT,
  user_id BIGINT NOT NULL, -- Discord user id
  guild_id BIGINT NOT NULL, -- Discord guild id
  channel_id BIGINT NOT NULL, -- Discord channel id
  join_time TIMESTAMP NOT NULL DEFAULT NOW(),
  leave_time TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
