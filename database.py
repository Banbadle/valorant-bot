import mysql.connector
import toml

class Database():
    def __init__(self):
        with open('config.toml', 'r') as f:
            config = toml.loads(f.read())

        try:
            self.connection = mysql.connector.connect(
                host=config['database']['hostname'],
                database=config['database']['database'],
                user=config['database']['rw']['user'],
                password=config['database']['rw']['password'],
            )
        except mysql.connector.Error:
            print('Database connection failed')

    def add_user(self, username, tag, mention_id):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO users (
                    username, tag, mention_id
                ) VALUES (
                    %s, %s, %s
                )
            ''', (username, tag, mention_id))
        self.connection.commit()

    def add_message(self, guild_id, channel_id, message_id, mention_id):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO messages (
                    guild_id, channel_id, message_id, created_by
                ) VALUES (
                    %s, %s, %s, (
                        SELECT id FROM users WHERE mention_id = %s
                    )
                )
            ''', (guild_id, channel_id, message_id, mention_id))
        self.connection.commit()

    def add_reaction(self, discord_message_id, mention_id, emoji):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO reactions (
                    message_id, user_id, emoji
                ) VALUES (
                    (
                        SELECT id FROM messages WHERE message_id = %s
                    ), (
                        SELECT id FROM users WHERE mention_id = %s
                    ), %s
                );
            ''', (discord_message_id, mention_id, emoji))
        self.connection.commit()

    def get_reactions(self, message_id):
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT r.emoji, u.mention_id
                FROM messages m
                JOIN reactions r
                    ON m.id = r.message_id
                JOIN users u
                    ON r.user_id = u.id
                WHERE m.message_id = %s
                    AND NOT r.removed
            ''', (message_id,))
            return cursor.fetchall()

    def get_latest_message(self, guild_id):
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT message_id
                FROM messages
                WHERE guild_id = %s
                ORDER BY created
                LIMIT 1;
            ''', (guild_id,))
            return cursor.fetchone()['message_id']
