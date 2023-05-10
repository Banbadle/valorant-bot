CREATE TABLE IF NOT EXISTS crediteventtypes (
  id INT NOT NULL AUTO_INCREMENT,
  event_name VARCHAR(255) NOT NULL,
  event_category VARCHAR(255) NOT NULL DEFAULT "Misc",
  default_value INT NOT NULL,
  cooldown INT NOT NULL DEFAULT 30,
  public BOOL NOT NULL DEFAULT TRUE,
  PRIMARY KEY (id)
);