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

#------------------------------------------------------------------------------
    # Users table functions
#------------------------------------------------------------------------------

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

    def set_timezone(self, user, timezone):
        if not self._get_user(user.id):
            self._add_user(user.name, user.discriminator, user.id)

        self._set_timezone(user.id, timezone)

    def get_timezone(self, user):
        if not self._get_user(user.id):
            self._add_user(user.name, user.discriminator, user.id)

        return self._get_timezone(user.id)

    def set_notifications(self, user, status):
        if not self._get_user(user.id):
            self._add_user(user.name, user.discriminator, user.id)

        self._set_notifications(user.id, status)

    def get_notifications(self, user):
        if not self._get_user(user.id):
            self._add_user(user.name, user.discriminator, user.id)

        return self._get_notifications(user.id)

    def get_users_to_notify(self, message_id):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT u.id
                FROM users u
                JOIN reactions r
                    ON u.id = r.user_id
                WHERE r.message_id = %s
                    AND r.removed IS NULL
                    AND u.notify = 1
            ''', (message_id,))
            result = cursor.fetchall()
            return result and list(r[0] for r in result)

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
                SET social_credit = social_credit + %s
                WHERE id = %s
            ''', (num, user.id))
        self.connection.commit()

    def _set_timezone(self, user_id, timezone):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                UPDATE users
                SET timezone = %s
                WHERE id = %s
            ''', (timezone, user_id))
        self.connection.commit()

    def _get_notifications(self, user_id):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT notify
                FROM users
                WHERE id = %s
                LIMIT 1
            ''', (user_id,))
            result = cursor.fetchone()
            return result is not None and result[0]

    def _set_notifications(self, user_id, status):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                UPDATE users
                SET notify = %s
                WHERE id = %s
            ''', (status, user_id))
        self.connection.commit()

    def _get_timezone(self, user_id):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT timezone
                FROM users
                WHERE id = %s
                LIMIT 1
            ''', (user_id,))
            result = cursor.fetchone()
            return result is not None and result[0]

#------------------------------------------------------------------------------
    # Messages table functions
#------------------------------------------------------------------------------

# MESSAGE TYPES:
# 0: Misc
# 1: Game Request
# 2: Check In
# 3: Credit Vote


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

    def get_active_messages(self, guild_id):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT id
                FROM messages
                WHERE guild_id = %s
                    AND ADDTIME(created, '06:00:00') > NOW();
                ORDER BY created DESC
            ''', (guild_id,))
            result = cursor.fetchall()
            return result and result[0]

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
        channel_id = self.get_channel_id(message_id)
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

    def get_current_time_reactions(self, react_stamp):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT r.message_id, r.user_id
                FROM messages m
                JOIN reactions r
                	ON m.id = r.message_id
                WHERE r.react_stamp = %s
                	AND r.removed IS NULL
                	AND ADDTIME(m.created, '12:30:00') > UTC_TIMESTAMP();
            ''', (react_stamp,))

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
#------------------------------------------------------------------------------

    def get_user_reaction(self, message_id, user_id):
        reaction = self._get_user_reaction(message_id, user_id)
        if not reaction:
            return
        return reaction['react_stamp']

    def add_reaction(self, message_id, user, react_stamp):
        if not self._get_user(user.id):
            self._add_user(user.name, user.discriminator, user.id)

        self._add_reaction(message_id, user.id, react_stamp)

    def remove_reaction(self, message_id, user_id, react_stamp):
        if not self._get_user(user_id):
            return

        self._remove_reaction(message_id, user_id, react_stamp)

    def get_reactions(self, message_id):
        self._refresh_connection()
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT r.react_stamp, u.id as user, r.created as timestamp
                FROM messages m
                JOIN reactions r
                    ON m.id = r.message_id
                JOIN users u
                    ON r.user_id = u.id
                WHERE m.id = %s
                    AND r.removed IS NULL
                ORDER BY r.react_stamp, r.created
            ''', (message_id,))
            return cursor.fetchall()

    def get_users_from_reaction(self, message_id, react_stamp):
        self.refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT user_id
                FROM reactions
                WHERE message_id = %s
                    AND react_stamp = %s
                    AND removed IS NULL
            ''', (message_id, react_stamp))
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

    def _add_reaction(self, message_id, user_id, react_stamp):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO reactions (
                    message_id, user_id, react_stamp
                ) VALUES (
                    %s, %s, %s
                ) ON DUPLICATE KEY UPDATE removed = NULL, created = UTC_TIMESTAMP();
            ''', (message_id, user_id, react_stamp))
        self.connection.commit()

    def _remove_reaction(self, message_id, user_id, react_stamp):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                UPDATE reactions
                SET removed = UTC_TIMESTAMP()
                WHERE message_id = %s
                    AND user_id = %s
                    AND react_stamp = %s
            ''', (message_id, user_id, react_stamp))
        self.connection.commit()
        
# -----------------------------------------------------------------------------
    # VoiceChannelLog table functions
# -----------------------------------------------------------------------------

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
                    AND r.react_stamp <> '❌'
                    AND r.message_id = %s
            ''', (message_id,))
            return cursor.fetchall()

    def user_leave(self, user, channel):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute('''
                UPDATE voicechannellog
                SET leave_time = UTC_TIMESTAMP()
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
        
#------------------------------------------------------------------------------
    # CreditEventTypes table functions
#------------------------------------------------------------------------------

    def modify_event(self, event_name, column_name, new_value):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE crediteventtypes
                SET {column_name} = %s
                WHERE event_name = %s;
            ''', (new_value, event_name))
        self.connection.commit()


    def add_credit_event_type(self, event_name, default_value, event_category="Misc", cooldown=10, public="TRUE"):
        self._refresh_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO crediteventtypes (
                    event_name, default_value, event_category, cooldown, public
                ) VALUES (
                    %s, %s, %s, %s, {public}
                )
            ''', (event_name, default_value, event_category, cooldown))
        self.connection.commit()
        
    def get_event_categories(self, is_reward=None):
        extra_str = ""
        if is_reward == 1:
            extra_str = "WHERE default_value > 0"
        elif is_reward == 0:
            extra_str = "WHERE default_value < 0"
        
        self._refresh_connection()
        
        with self.connection.cursor() as cursor:
            cursor.execute(f'SELECT DISTINCT event_category FROM crediteventtypes {extra_str}')
            
            results = cursor.fetchall()
            return list(r[0] for r in results)
        
    def get_event_types_from_category(self, category):
        self._refresh_connection()
        
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT event_name
                FROM crediteventtypes
                WHERE event_category = %s
            ''', (category,))
            
            results = cursor.fetchall()
            return list(r[0] for r in results)
        
    def get_event_details(self, event_name):
        self._refresh_connection()
        
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT default_value, cooldown
                FROM crediteventtypes
                WHERE event_name = %s
            ''', (event_name,))
            
            result = cursor.fetchone()
            if result is not None:
                return result
            
    def get_event_value(self, event_name):
        self._refresh_connection()
        
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT default_value
                FROM crediteventtypes
                WHERE event_name = %s
            ''', (event_name,))
            
            result = cursor.fetchone()
            if result is not None:
                return int(result[0])
        
    def get_event_cooldown(self, event_name):
        self._refresh_connection()
        
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT cooldown
                FROM crediteventtypes
                WHERE event_name = %s
            ''', (event_name,))
            
            result = cursor.fetchone()
            if result is not None:
                return int(result[0])
            
#------------------------------------------------------------------------------
    # CreditChanges table functions
#------------------------------------------------------------------------------

    def record_credit_change(self, 
                             user, 
                             event_name, 
                             change_value,
                             cooldown=0, 
                             vote_msg_id=None,
                             cause_user=None, 
                             processed=None):
        
        if user and not self._get_user(user.id):
            self._add_user(user.name, user.discriminator, user.id)
            
        if cause_user and not self._get_user(cause_user.id):
            self._add_user(cause_user.name, cause_user.discriminator, cause_user.id)

        self._record_credit_change(user, 
                                   event_name, 
                                   change_value, 
                                   cooldown, 
                                   vote_msg_id, 
                                   cause_user, 
                                   processed)
        
    def _record_credit_change(self, 
                             user, 
                             event_name, 
                             change_value,
                             cooldown=0, 
                             vote_msg_id=None,
                             cause_user=None, 
                             processed=None):
        self._refresh_connection()
        
        with self.connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO creditchanges (
                    user_id, 
                    event_name, 
                    change_value,
                    vote_msg_id,
                    cause_user_id,
                    processed,
                    end_time
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, UTC_TIMESTAMP() + INTERVAL %s MINUTE
                )
            ''', (user.id, event_name, change_value, vote_msg_id, cause_user.id, processed, cooldown))
        self.connection.commit()
        
    def process_credit_change(self, vote_msg_id, processed, verdict_msg_id):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                UPDATE creditchanges
                SET processed = %s,
                    verdict_msg_id = %s
                WHERE vote_msg_id = %s
            ''', (processed, verdict_msg_id, vote_msg_id))
        self.connection.commit()
        
#------------------------------------------------------------------------------
    # CreditVotes table functions
#------------------------------------------------------------------------------    

    def set_user_vote(self, message_id, user, vote):
        if not self._get_user(user.id):
            self._add_user(user.name, user.discriminator, user.id)

        self._set_user_vote(message_id, user, vote) 

    def _set_user_vote(self, message_id, user, vote):
        self._refresh_connection()
        
        with self.connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO creditvotes (
                    message_id, user_id, vote
                ) VALUES (
                    %s, %s, %s
                )
            ''', (message_id, user.id, vote))
        self.connection.commit()
        
    def get_user_vote(self, message_id, user_id):
        self._refresh_connection()
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute('''
                SELECT vote
                FROM creditvotes
                WHERE message_id = %s
                    AND user_id = %s
            ''', (message_id, user_id))
            result = cursor.fetchone()
            if result is not None:
                return result['vote']
        
    def get_votes(self, message_id):
        self._refresh_connection()
        
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT vote
                FROM creditvotes
                WHERE message_id = %s
            ''', (message_id,))
            
            results = cursor.fetchall()
            return list(int(r[0]) for r in results)
        