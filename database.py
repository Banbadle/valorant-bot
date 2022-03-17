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
        except mysql.connector.Error as e:
            print(f"Database connection failed: {e}")

    def _refresh_connection(self):
        if self.connection.is_connected():
            return
        self._connect()

    # Users table functions

    def get_valorant_username(self, user_id):
        self._refresh_connection()
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT val_username, val_tag
                FROM users
                WHERE id = %s
                LIMIT 1
            ''', (user_id,))
            return cursor.fetchone()

    def set_valorant_username(self, user_id, username, tag):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                UPDATE users
                SET val_username = %s,
                    val_tag = %s
                WHERE id = %s
            ''', (username, tag, user_id))
        self.connection.commit()

    def get_social_credit(self, user_id):
        self._refresh_connection()
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT social_credit
                FROM users
                WHERE id = %s
                LIMIT 1
            ''', (user_id,))
            result = cursor.fetchone()
            return result and result['social_credit']

    def add_social_credit(self, user, num):
        if not self._get_user(user.id):
            self._add_user(user.name, user.discriminator, user.id)

        self._add_social_credit(user, num)

    def is_admin(self, user_id):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT is_admin
                FROM users
                WHERE id = %s
                LIMIT 1
            ''', (user_id,))
            result = cursor.fetchone()
            return result is not None and result[0] == 1

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

    def _add_social_credit(self, user, num):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                UPDATE users
                SET social_credit = social_credit + %s,
                WHERE id = %s
            ''', (num, user.id))
        self.connection.commit()

    # Messages table functions

    def add_message(self, message, trigger, message_type = 0):
        author = trigger.author
        if not self._get_user(author.id):
            self._add_user(author.name, author.discriminator, author.id)

        self._add_message(message.guild.id, message.channel.id, message.id, author.id, trigger.id, message_type)

    def get_latest_message(self, guild_id):
        self._refresh_connection()
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT id
                FROM messages
                WHERE guild_id = %s
                ORDER BY created DESC
                LIMIT 1;
            ''', (guild_id,))
            result = cursor.fetchone()
            return result and result['id']

    def get_message_from_trigger(self, trigger_id):
        self._refresh_connection()
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT id
                FROM messages
                WHERE trigger_msg = %s
                ORDER BY created
                LIMIT 1;
            ''', (trigger_id,))
            return cursor.fetchone()

    def get_message_type(self, message_id):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT message_type
                FROM messages
                WHERE id = %s
                LIMIT 1;
            ''', (message_id,))
            result = cursor.fetchone()
            return result and result[0]

    def get_channel_id(self, message_id):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT channel_id
                FROM messages
                WHERE id = %s
                LIMIT 1;
            ''', (message_id,))
            result = cursor.fetchone()
            return result and result[0]
        
    def is_message_in_db(self, message_id):
        channel_id = self.get_channel_id(self, message_id)
        return bool(channel_id)

    def _add_message(self, guild_id, channel_id, message_id, user_id, trigger_id, message_type):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO messages (
                    id, guild_id, channel_id, created_by, trigger_msg, message_type
                ) VALUES (
                    %s, %s, %s, %s, %s, %s
                )
            ''', (message_id, guild_id, channel_id, user_id, trigger_id, message_type))
        self.connection.commit()

#------------------------------------------------------------------------------
    def get_current_time_reactions(self, emoji):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT r.message_id, r.user_id
                FROM messages m
                JOIN reactions r
                	ON m.id = r.message_id
                WHERE r.emoji = %s
                	AND r.removed IS NULL
                	AND ADDTIME(m.created, '12:30:00') > NOW();
            ''', (emoji,))
            return cursor.fetchall()

    def get_guild_id(self, message_id):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT guild_id
                FROM messages
                WHERE id = %s
                LIMIT 1;
            ''', (message_id,))
            result = cursor.fetchone()
            return result and result[0]

    def get_creation_time(self, message_id):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT created
                FROM messages
                WHERE id = %s
            ''', (message_id,))
            result = cursor.fetchone()
            return result and result[0]

    def get_creator(self, message_id):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT created_by
                FROM messages
                WHERE id = %s
            ''', (message_id,))
            result = cursor.fetchone()
            return result and result[0]
#------------------------------------------------------------------------------

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
                SELECT r.emoji, u.id as user
                FROM messages m
                JOIN reactions r
                    ON m.id = r.message_id
                JOIN users u
                    ON r.user_id = u.id
                WHERE m.id = %s
                    AND r.removed IS NULL
            ''', (message_id,))
            return cursor.fetchall()

# -----------------------------------------------------------------------------
    def get_users_from_reaction(self, message_id, emoji):
        self.refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT user_id
                FROM reactions
                WHERE message_id = %s
                    AND emoji = %s
                    AND removed IS NULL
            ''', (message_id, emoji))
            return cursor.fetchall()
# -----------------------------------------------------------------------------
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

    # VoiceChannelLog table functions

    def user_join(self, user, channel):
        if not self._get_user(user.id):
            self._add_user(user.name, user.discriminator, user.id)

        self._user_join(user, channel)

    def get_users_in_voice(self, message_id):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT r.user_id, v.channel_id
                FROM reactions r
                JOIN voicechannellog v
                    ON v.user_id = r.user_id
                WHERE v.leave_time IS NULL
                    AND r.removed IS NULL
                    AND r.emoji <> '❌'
                    AND r.message_id = %s
            ''', (message_id))
            return cursor.fetchall()

    def user_leave(self, user, channel):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                UPDATE voicechannellog
                SET leave_time = NOW()
                WHERE user_id = %s
                    AND channel_id = %s
            ''', (user.id, channel.id))
        self.connection.commit()

    def get_user_voice_channel(self, user_id):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT channel_id
                FROM voicechannellog
                WHERE user_id = %s
                    AND leave_time IS NULL
                LIMIT 1
            ''', (user_id,))
            return cursor.fetchone()

    def get_user_voice_guild(self, user_id):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT guild_id
                FROM voicechannellog
                WHERE user_id = %s
                    AND leave_time IS NULL
                LIMIT 1
            ''', (user_id,))
            return cursor.fetchone()

    def _user_join(self, user, channel):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO voicechannellog (
                    user_id, guild_id, channel_id
                ) VALUES (
                    %s, %s, %s
                )
            ''', (user.id, channel.guild.id, channel.id))
        self.connection.commit()
