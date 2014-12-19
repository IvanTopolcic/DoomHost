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


# This class handles all database related information
class MySQL:
    def __init__(self, hostname, username, password, database):
        self._hostname = hostname
        self._username = username
        self._password = password
        self._database = database

    def connect(self):
        return pymysql.connect(host=self._hostname, user=self._username, passwd=self._password, db=self._database)

    def get_user(self, username):
        connection = self.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM `login` WHERE `username` = %s", username)
        return cursor.fetchone()