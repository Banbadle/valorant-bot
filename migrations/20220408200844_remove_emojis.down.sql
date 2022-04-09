START TRANSACTION;

ALTER TABLE `users`
DROP `timezone`;

ALTER TABLE `reactions`
DROP FOREIGN KEY `fk_message_id`;

DROP INDEX `message_user_time` ON `reactions`;

ALTER TABLE `reactions`
ADD `emoji` CHAR(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
DROP `react_stamp`,
ADD UNIQUE `message_id` (`message_id`, `user_id`, `emoji`),
ADD FOREIGN KEY `reactions_ibfk_1` (message_id) REFERENCES messages(id) ON DELETE CASCADE;

ALTER TABLE `users`
RENAME INDEX `discord_user` TO `username`,
RENAME INDEX `valorant_user` TO `val_username`;

ALTER TABLE `messages`
DROP FOREIGN KEY `fk_created_by`;

ALTER TABLE `messages`
ADD FOREIGN KEY `messages_ibfk_1` (created_by) REFERENCES users(id);

ALTER TABLE `reactions`
DROP FOREIGN KEY `fk_reactions_user_id`;

ALTER TABLE `reactions`
ADD FOREIGN KEY `reactions_ibfk_2` (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE `voicechannellog`
DROP FOREIGN KEY `fk_voice_user_id`;

ALTER TABLE `voicechannellog`
ADD FOREIGN KEY `voicechannellog_ibfk_1` (user_id) REFERENCES users(id) ON DELETE CASCADE;

COMMIT;
