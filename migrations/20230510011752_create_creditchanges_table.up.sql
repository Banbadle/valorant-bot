CREATE TABLE IF NOT EXISTS creditchanges (
  id INT NOT NULL AUTO_INCREMENT,
  user_id BIGINT NOT NULL, -- Discord user id
  event_name VARCHAR(255) NOT NULL,
  change_value BIGINT NOT NULL,
  start_time TIMESTAMP NOT NULL DEFAULT UTC_TIMESTAMP(),
  vote_msg_id BIGINT, -- Discord message id
  processed BOOL DEFAULT 1,
  end_time TIMESTAMP NOT NULL DEFAULT UTC_TIMESTAMP(),  -- alt: ADDTIME(UTC_TIMESTAMP(), "0:30:0"),
  verdict_msg_id BIGINT, -- Discord message id
  PRIMARY KEY (id),
  FOREIGN KEY `fk_creditchanges_user_id` (user_id) REFERENCES users(id) ON DELETE CASCADE,
);