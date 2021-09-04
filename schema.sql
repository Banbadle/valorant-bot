CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(255) NOT NULL,
  tag SMALLINT(255) NOT NULL,
  mention_id VARCHAR(255) NOT NULL UNIQUE,
  social_credit INT NOT NULL DEFAULT 0,
  -- on time and not on time
  created TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (id)
);

CREATE TABLE messages (
  id INT NOT NULL AUTO_INCREMENT,
  guild_id INT NOT NULL,
  channel_id INT NOT NULL,
  message_id INT NOT NULL,
  created_by INT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT NOW(),
  FOREIGN KEY (created_by) REFERENCES users(id),
  PRIMARY KEY (id)
);

CREATE TABLE reactions (
  id INT NOT NULL AUTO_INCREMENT,
  message_id INT NOT NULL,
  user_id INT NOT NULL,
  emoji VARCHAR(255) NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT NOW(),
  removed TIMESTAMP DEFAULT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (message_id) REFERENCES messages(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);