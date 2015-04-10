# Copyright (C) 2014 BestEver
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pymysql
import bcrypt
from time import time


# This class handles all database related information
class MySQL:
    def __init__(self, doomhost):
        self.doomhost = doomhost
        self._hostname = doomhost.settings['mysql']['hostname']
        self._username = doomhost.settings['mysql']['username']
        self._password = doomhost.settings['mysql']['password']
        self._database = doomhost.settings['mysql']['database']

    def connect(self):
        return pymysql.connect(host=self._hostname, user=self._username, passwd=self._password, db=self._database, autocommit=True)

    # -------------------------------------------------------------------------------------------- #
    # ----------------------------------- User Functions ----------------------------------------- #
    # -------------------------------------------------------------------------------------------- #

    def check_login(self, username, password):
        user = self.get_user(username)
        if user is None:
            return False
        if bcrypt.hashpw(password.encode('utf-8'), user['password'].encode('utf-8')) != user['password'].encode('utf-8'):
            return False
        return True


    def create_user(self, username, password, email):
        connection = self.connect()
        cursor = connection.cursor()
        return cursor.execute("INSERT INTO `login` (`username`, `password`, `email`, `level`, `activated`, `server_limit`, `remember_token`) \
            VALUES (%s, %s, %s, 1, 0, 4, null)", (username, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14))))

    def update_server_limit(self, user_id, server_limit):
        connection = self.connect()
        cursor = connection.cursor()
        return cursor.execute("UPDATE `login` SET `server_limit` = %s WHERE `id` = %s", (server_limit, user_id))

    def update_password(self, user_id, password):
        connection = self.connect()
        cursor = connection.cursor()
        return cursor.execute("UPDATE `login` SET `password` = %s WHERE `id` = %s",
            ((bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14)), user_id)))

    def set_activated(self, user_id):
        connection = self.connect()
        cursor = connection.cursor()
        return cursor.execute("UPDATE `login` SET `activated` = 1 WHERE `id` = %s", user_id)

    def get_user(self, username):
        connection = self.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT `id`, `username`, `password`, `level`, `activated`, `server_limit` FROM `login` WHERE `username` = %s", username)
        return cursor.fetchone()

    # -------------------------------------------------------------------------------------------- #
    # ----------------------------------- Server Functions --------------------------------------- #
    # -------------------------------------------------------------------------------------------- #

    def add_server(self, user_id, unique_id, wads):
        connection = self.connect()
        cursor = connection.cursor()
        if cursor.execute("INSERT INTO `servers` (`unique_id`, `user_id`, `time_started`, `online`, `listener`) VALUES (%s, %s, %s, 0, %s)",
            (unique_id, user_id, time(), self.doomhost.settings['network']['listener_id'])):
            insertion_id = cursor.lastrowid
            for wad in wads:
                cursor.execute("INSERT INTO `servers_wads` (`server_id`, `name`) VALUES (%s, %s)", (insertion_id, wad))

    def update_port(self, unique_id, port):
        connection = self.connect()
        cursor = connection.cursor()
        return cursor.execute("UPDATE `servers` SET `port` = %s WHERE `unique_id` = %s", (port, unique_id))

    # Toggles a server between online and offline
    # This is used twice -- once when the server starts, and once when it stops
    def toggle_online(self, unique_id):
        connection = self.connect()
        cursor = connection.cursor()
        return cursor.execute("UPDATE `servers` SET `online` = (1 - `online`) WHERE `unique_id` = %s", unique_id)
