import mysql.connector
import toml

class Database():
    def __init__(self):
        with open('config.toml', 'r') as f:
            self.config = toml.loads(f.read())

        self._connect()

    def _connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.config['database']['hostname'],
                database=self.config['database']['database'],
                user=self.config['database']['rw']['user'],
                password=self.config['database']['rw']['password'],
            )
        except mysql.connector.Error:
            print('Database connection failed')
        
    def _refresh_connection(self):
        if self.connection.is_connected():
            return
        self._connect()

    # Users table functions

    def _get_user(self, user_id):
        self._refresh_connection()
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT *
                FROM users
                WHERE id = %s
            ''', (user_id,))
            return cursor.fetchone()

    def _add_user(self, username, tag, user_id):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO users (
                    id, username, tag
                ) VALUES (
                    %s, %s, %s
                )
            ''', (user_id, username, tag))
        self.connection.commit()

    # Messages table functions

    def add_message(self, message, author):
        if not self._get_user(author.id):
            self._add_user(author.name, author.discriminator, author.id)

        self._add_message(message.guild.id, message.channel.id, message.id, author.id)

    def get_latest_message(self, guild_id):
        self._refresh_connection()
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT id
                FROM messages
                WHERE guild_id = %s
                ORDER BY created
                LIMIT 1;
            ''', (guild_id,))
            return cursor.fetchone()['id']

    def _add_message(self, guild_id, channel_id, message_id, user_id):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO messages (
                    id, guild_id, channel_id, created_by
                ) VALUES (
                    %s, %s, %s, %s
                )
            ''', (message_id, guild_id, channel_id, user_id))
        self.connection.commit()

    # Reactions table functions

    def get_user_reaction(self, message_id, user_id):
        reaction = self._get_user_reaction(message_id, user_id)
        if not reaction:
            return
        return reaction['emoji']

    def add_reaction(self, message_id, user, emoji):
        if not self._get_user(user.id):
            self._add_user(user.name, user.discriminator, user.id)

        self._add_reaction(message_id, user.id, emoji)

    def remove_reaction(self, message_id, user_id, emoji):
        if not self._get_user(user_id):
            return

        self._remove_reaction(message_id, user_id, emoji)

    def get_reactions(self, message_id):
        self._refresh_connection()
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT r.emoji, u.id
                FROM messages m
                JOIN reactions r
                    ON m.id = r.message_id
                JOIN users u
                    ON r.user_id = u.id
                WHERE m.id = %s
                    AND r.removed IS NULL
            ''', (message_id,))
            return cursor.fetchall()

    def _get_user_reaction(self, message_id, user_id):
        self._refresh_connection()
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT *
                FROM reactions
                WHERE message_id = %s
                    AND user_id = %s
                    AND removed IS NULL
            ''', (message_id, user_id))
            return cursor.fetchone()

    def _add_reaction(self, message_id, user_id, emoji):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO reactions (
                    message_id, user_id, emoji
                ) VALUES (
                    %s, %s, %s
                ) ON DUPLICATE KEY UPDATE removed = NULL
            ''', (message_id, user_id, emoji))
        self.connection.commit()

    def _remove_reaction(self, message_id, user_id, emoji):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                UPDATE reactions
                SET removed = NOW()
                WHERE message_id = %s
                    AND user_id = %s
                    AND emoji = %s
            ''', (message_id, user_id, emoji))
        self.connection.commit()
