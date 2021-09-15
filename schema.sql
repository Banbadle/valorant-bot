CREATE TABLE IF NOT EXISTS users (
  id INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(255) NOT NULL,
  tag SMALLINT(255) NOT NULL,
  mention_id VARCHAR(255) NOT NULL UNIQUE,
  social_credit INT NOT NULL DEFAULT 0,
  val_username VARCHAR(255)
  val_tag VARCHAR(255)
  -- on time and not on time
  created TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (id),
  UNIQUE (username, tag),
  UNIQUE (val_username, val_tag)
);

CREATE TABLE IF NOT EXISTS messages (
  id INT NOT NULL AUTO_INCREMENT,
  guild_id INT NOT NULL,
  channel_id INT NOT NULL,
  message_id INT NOT NULL,
  created_by INT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT NOW(),
  FOREIGN KEY (created_by) REFERENCES users(id),
  PRIMARY KEY (id),
  UNIQUE (guild_id, channel_id, message_id)
);

CREATE TABLE IF NOT EXISTS reactions (
  id INT NOT NULL AUTO_INCREMENT,
  message_id INT NOT NULL,
  user_id INT NOT NULL,
  emoji VARCHAR(255) NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT NOW(),
  removed BIT(1) DEFAULT 0 NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
