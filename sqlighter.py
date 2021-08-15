import sqlite3


class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def update_firstname(self, user_id, status,chat_id):
        """фамилия"""
        with self.connection:
            return self.cursor.execute(f"UPDATE `{chat_id}` SET `first_name` = ? WHERE `user_id` = ?", (status, user_id))


    def get_balance(self, user_id,chat_id):
        """Получаем сколько раз писал мат"""
        with self.connection:
            return self.cursor.execute(f'SELECT balance FROM `{chat_id}` WHERE `user_id` = ?', (user_id,)).fetchall()

    def get_bonus(self, user_id,chat_id):
        """Получаем сколько раз писал мат"""
        with self.connection:
            return self.cursor.execute(f'SELECT bonus FROM `{chat_id}` WHERE `user_id` = ?', (user_id,)).fetchall()

    def get_time_bonus(self, user_id,chat_id):
        """Получаем сколько раз писал мат"""
        with self.connection:
            return self.cursor.execute(f'SELECT time_bonus FROM `{chat_id}` WHERE `user_id` = ?', (user_id,)).fetchall()


    def get_medal(self, user_id,chat_id):
        """Получаем сколько раз писал мат"""
        with self.connection:
            return self.cursor.execute(f'SELECT medal FROM `{chat_id}` WHERE `user_id` = ?', (user_id,)).fetchall()
    def get_top(self,chat_id):
        with self.connection:
            return self.cursor.execute(f'SELECT * FROM `{chat_id}` ORDER BY `medal` DESC , `balance` DESC' , ()).fetchall()

    def subscriber_exists(self, user_id,chat_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute(f'SELECT * FROM `{chat_id}` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id, chat_id,status=True):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute(f"INSERT INTO `{chat_id}` (`user_id`, `status`) VALUES(?,?)", (user_id, status))


    def update_balance(self, user_id,status,chat_id):
        """Обновляем количество мата пользователя"""
        with self.connection:
            return self.cursor.execute(f"UPDATE `{chat_id}` SET `balance` = ? WHERE `user_id` = ?", (status, user_id))
    def update_medal(self, user_id,status,chat_id ):
        """Обновляем количество мата пользователя"""
        with self.connection:
            return self.cursor.execute(f"UPDATE `{chat_id}` SET `medal` = ? WHERE `user_id` = ?", (status, user_id))

    def update_bonus(self, user_id, status,chat_id):
        with self.connection:
            return self.cursor.execute(f"UPDATE `{chat_id}` SET `bonus` = ? WHERE `user_id` = ?", (status, user_id))

    def update_time_bonus(self, user_id,status, chat_id):
        """Обновляем количество мата пользователя"""
        with self.connection:
            return self.cursor.execute(f"UPDATE `{chat_id}` SET `time_bonus` = ? WHERE `user_id` = ?", (status, user_id))

    def create_table_for_char(self,chat_id):
        with self.connection:
            return self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {chat_id}(user_id CHAR, status BOOLEAN, first_name CHAR,balance INT,bonus BOOLEAN,time_bonus DATE, medal INT DEFAULT 0 )")

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
