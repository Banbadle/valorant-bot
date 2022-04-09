START TRANSACTION;

ALTER TABLE `users`
ADD `timezone` VARCHAR(255) DEFAULT 'Europe/London';

ALTER TABLE `reactions`
DROP FOREIGN KEY `reactions_ibfk_1`;

DROP INDEX `message_id` ON `reactions`;

ALTER TABLE `reactions`
DROP `emoji`,
ADD `react_stamp` BIGINT NOT NULL,
ADD UNIQUE `message_user_time` (`message_id`, `user_id`, `react_stamp`),
ADD FOREIGN KEY `fk_message_id` (message_id) REFERENCES messages(id) ON DELETE CASCADE;

-- Giving indexes and foreign keys names, really should have done this initially
ALTER TABLE `users`
RENAME INDEX `username` TO `discord_user`,
RENAME INDEX `val_username` TO `valorant_user`;

ALTER TABLE `messages`
DROP FOREIGN KEY `messages_ibfk_1`;

ALTER TABLE `messages`
ADD FOREIGN KEY `fk_created_by` (created_by) REFERENCES users(id);

ALTER TABLE `reactions`
DROP FOREIGN KEY `reactions_ibfk_2`;

ALTER TABLE `reactions`
ADD FOREIGN KEY `fk_reactions_user_id` (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE `voicechannellog`
DROP FOREIGN KEY `voicechannellog_ibfk_1`;

ALTER TABLE `voicechannellog`
ADD FOREIGN KEY `fk_voice_user_id` (user_id) REFERENCES users(id) ON DELETE CASCADE;

COMMIT;
