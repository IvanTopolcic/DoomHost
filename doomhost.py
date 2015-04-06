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
import os.path
import threading
import atexit
from mysql import mysql
from net import tcplistener
from output.printlogger import *

# The main DoomHost class
# Controls general startup as well as server addition/removal
class DoomHost:

    # A list containing all of our server objects
    servers = []

    def __init__(self):
        # This needs to be called or else colored outputs won't work on windows
        init()
        # Attempt to load configuration file
        try:
            # Check to see if they specify a custom configuration file
            if len(sys.argv) > 1:
                config = open(sys.argv[1], 'r')
            else:
                config = open('config.json', 'r')
            self.settings = json.load(config)
            # User has not filled out the secret
            if self.settings['network']['secret'] == "fill this in with something random":
                log(LEVEL_ERROR, "Please change the Network Secret in the configuration file.")
                sys.exit(1)
            log(LEVEL_OK, "Loaded configuration file.")
        except FileNotFoundError as e:
            log(LEVEL_ERROR, "Configuration file not found. \
                Please create a config.json or run with: python doomhost.py your_config.json")
            sys.exit(1)
        # Check if a logfile is present and create one if not
        if not os.path.isfile("logfile.txt"):
            open("logfile.txt", 'w+')
            log(LEVEL_OK, "Created logfile.txt")
        # Check to see if mysql database settings are correct
        self.db = mysql.MySQL(self.settings['mysql']['hostname'],
                              self.settings['mysql']['username'],
                              self.settings['mysql']['password'],
                              self.settings['mysql']['database'])
        try:
            self.db.connect()
        except mysql.pymysql.MySQLError as e:
            log(LEVEL_ERROR, "MySQL configuration error: {}".format(e))
            sys.exit(1)
        log(LEVEL_OK, "MySQL connection succeeded!")
        # Attempt to start our TCP server
        self.tcp_listener = tcplistener.TCPListener(self, self.settings['network']['hostname'],
                                                self.settings['network']['port'],
                                                self.settings['network']['secret'])
        atexit.register(_cleanup, self)
        threading.Thread(target=self.tcp_listener.serve).run()

    # Checks if an object is a number, and whether or not its in our port range
    def is_valid_port(self, port):
        try:
            val = int(port)
        except ValueError:
            return False
        if port > self.settings['zandronum']['max_port'] or port < self.settings['zandronum']['min_port']:
            return False
        return True

    # Retrieves a server on given port
    def get_server(self, port):
        for server in self.servers:
            if server.port == port:
                return server
        return None

    # Removes a server from our list
    def remove_server(self, server):
        self.servers.remove(server)

    # Adds a server to our list
    def add_server(self, server):
        self.servers.append(server)

    # Gets the first free port
    def get_first_free_port(self):
        for temp_port in range(self.settings['zandronum']['min_port'], self.settings['zandronum']['max_port']):
            if self.get_server(temp_port) is None:
                return temp_port
        return None


# Shutdown hook
def _cleanup(doomhost):
    log(LEVEL_STATUS, "Cleaning up...")
    doomhost.tcp_listener.socket.close()
    for server in doomhost.servers:
        server.process.kill_server()

try:
    host = DoomHost()
except KeyboardInterrupt:
    # Ignore keyboard interrupt stacktraces
    pass
