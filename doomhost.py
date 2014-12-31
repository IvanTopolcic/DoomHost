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

import json
import sys
from mysql import mysql
from net import tcplistener
import threading
import atexit


class DoomHost:
    def __init__(self):
        # Attempt to load configuration file
        try:
            # Check to see if they specify a custom configuration file
            if sys.argv[1] is not None:
                config = open(sys.argv[1], 'r')
            else:
                config = open('config.json', 'r')
            self.settings = json.load(config)
            # User has not filled out the secret, generate one randomly for them
            if self.settings['network']['secret'] == "fill this in with something random":
                print("Please change the Network Secret in the configuration file.")
                sys.exit(1)
            print("Loaded configuration file.")
        except FileNotFoundError as e:
            print("Configuration file not found. Please create a config.json or run with: python doomhost.py your_config.json")
            print(e)
            sys.exit(1)
        # Check to see if mysql database settings are correct
        self.db = mysql.MySQL(self.settings['mysql']['hostname'],
                                self.settings['mysql']['username'],
                                self.settings['mysql']['password'],
                                self.settings['mysql']['database'])
        try:
            self.db.connect()
        except mysql.pymysql.MySQLError as e:
            print("MySQL configuration error: {}".format(e))
            sys.exit(1)
        print("MySQL connection succeeded!")
        # Attempt to start our TCP server
        self.tcp_listener = tcplistener.TCPListener(self, self.settings['network']['hostname'],
                                                self.settings['network']['port'],
                                                self.settings['network']['secret'])
        atexit.register(_cleanup, self.tcp_listener)
        threading.Thread(target=self.tcp_listener.serve).run()

# Shutdown hook
def _cleanup(tcp_listener):
    tcp_listener.socket.close()
    print("\nCleaning up...")

try:
    host = DoomHost()
except KeyboardInterrupt:
    # Ignore keyboard interrupt stacktraces
    pass
