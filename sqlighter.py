import sqlite3


class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def update_firstname(self, user_id, status):
        """фамилия"""
        with self.connection:
            return self.cursor.execute("UPDATE `userdata` SET `first_name` = ? WHERE `user_id` = ?", (status, user_id))



    def get_balance(self, user_id):
        """Получаем сколько раз писал мат"""
        with self.connection:
            return self.cursor.execute('SELECT balance FROM `userdata` WHERE `user_id` = ?', (user_id,)).fetchall()

    def get_bonus(self, user_id):
        """Получаем сколько раз писал мат"""
        with self.connection:
            return self.cursor.execute('SELECT bonus FROM `userdata` WHERE `user_id` = ?', (user_id,)).fetchall()

    def get_time_bonus(self, user_id):
        """Получаем сколько раз писал мат"""
        with self.connection:
            return self.cursor.execute('SELECT time_bonus FROM `userdata` WHERE `user_id` = ?', (user_id,)).fetchall()

    def get_years_bonus(self, user_id):
        """Получаем сколько раз писал мат"""
        with self.connection:
            return self.cursor.execute('SELECT years FROM `userdata` WHERE `user_id` = ?', (user_id,)).fetchall()

    def get_month_bonus(self, user_id):
        """Получаем сколько раз писал мат"""
        with self.connection:
            return self.cursor.execute('SELECT month FROM `userdata` WHERE `user_id` = ?', (user_id,)).fetchall()

    def get_day_bonus(self, user_id):
        """Получаем сколько раз писал мат"""
        with self.connection:
            return self.cursor.execute('SELECT day FROM `userdata` WHERE `user_id` = ?', (user_id,)).fetchall()

    def get_hours_bonus(self, user_id):
        """Получаем сколько раз писал мат"""
        with self.connection:
            return self.cursor.execute('SELECT hours FROM `userdata` WHERE `user_id` = ?', (user_id,)).fetchall()

    def get_minutes_bonus(self, user_id):
        """Получаем сколько раз писал мат"""
        with self.connection:
            return self.cursor.execute('SELECT minutes FROM `userdata` WHERE `user_id` = ?', (user_id,)).fetchall()



    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `userdata` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id, status=True):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `userdata` (`user_id`, `status`) VALUES(?,?)", (user_id, status))

    def update_mat(self, user_id, status):
        """Обновляем количество мата пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `userdata` SET `mat` = ? WHERE `user_id` = ?", (status, user_id))

    def update_balance(self, user_id, status):
        """Обновляем количество мата пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `userdata` SET `balance` = ? WHERE `user_id` = ?", (status, user_id))

    def update_bonus(self, user_id, status):
        with self.connection:
            return self.cursor.execute("UPDATE `userdata` SET `bonus` = ? WHERE `user_id` = ?", (status, user_id))

    def update_time_bonus(self, user_id, status):
        """Обновляем количество мата пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `userdata` SET `time_bonus` = ? WHERE `user_id` = ?", (status, user_id))

    def update_years_bonus(self, user_id, status):
        """Обновляем количество мата пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `userdata` SET `years` = ? WHERE `user_id` = ?", (status, user_id))
    def update_month_bonus(self, user_id, status):
        with self.connection:
            return self.cursor.execute("UPDATE `userdata` SET `years` = ? WHERE `user_id` = ?", (status, user_id))

    def update_day_bonus(self, user_id, status):
        """Обновляем количество мата пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `userdata` SET `day` = ? WHERE `user_id` = ?", (status, user_id))

    def update_hours_bonus(self, user_id, status):
        """Обновляем количество мата пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `userdata` SET `hours` = ? WHERE `user_id` = ?", (status, user_id))

    def update_minutes_bonus(self, user_id, status):
        """Обновляем количество мата пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `userdata` SET `minutes` = ? WHERE `user_id` = ?", (status, user_id))

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()