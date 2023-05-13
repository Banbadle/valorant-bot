CREATE TABLE IF NOT EXISTS creditvotes (
  id INT NOT NULL AUTO_INCREMENT,
  message_id BIGINT NOT NULL, -- Discord message id
  user_id BIGINT NOT NULL, -- Discord user id
  vote BOOL NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT UTC_TIMESTAMP(),
  PRIMARY KEY (id),
  UNIQUE `message_user_time` (message_id, user_id)
);