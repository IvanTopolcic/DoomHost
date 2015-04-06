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


# This class handles all database related information
class MySQL:
    def __init__(self, hostname, username, password, database):
        self._hostname = hostname
        self._username = username
        self._password = password
        self._database = database

    def connect(self):
        return pymysql.connect(host=self._hostname, user=self._username, passwd=self._password, db=self._database, autocommit=True)

    # Returns True on successful insertion
    def create_user(self, username, password):
        connection = self.connect()
        cursor = connection.cursor()
        return cursor.execute("INSERT INTO `login` (`username`, `password`, `level`, `activated`, `server_limit`, `remember_token`) \
            VALUES (%s, %s, 1, 0, 4, null)", (username, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14))))



    def get_user(self, username):
        connection = self.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM `login` WHERE `username` = %s", username)
        return cursor.fetchone()
