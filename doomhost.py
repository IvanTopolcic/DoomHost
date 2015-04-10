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

import uuid
import platform
import json
import sys
import os.path
import threading
import atexit
import signal
import doom.servermonitor
from database import mysql
from net import tcplistener
from output.printlogger import *

working = False

# The main DoomHost class
# Controls general startup as well as server addition/removal
class DoomHost:

    # A list containing all of our server objects
    servers = []
    working = True

    # Uploaded file types
    FILETYPE_WAD = 0
    FILETYPE_IWAD = 1
    FILETYPE_CFG = 2

    # A dict containing valid extensions for filetypes
    allowed_extensions = {
        FILETYPE_WAD  : ['wad', 'pk3'],
        FILETYPE_IWAD : ['wad'],
        FILETYPE_CFG  : ['cfg', 'txt']
    }

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
            if self.settings['network']['secret'] == "" :
                log(LEVEL_ERROR, "Please change the Network Secret in the configuration file to a random string.")
                sys.exit(1)
            log(LEVEL_OK, "Loaded configuration file.")
        except FileNotFoundError as e:
            log(LEVEL_ERROR, "Configuration file not found. \
                Please create a config.json or run with: python doomhost.py your_config.json")
            sys.exit(1)
        # Set a mapping of constants to their directory location
        self.filetype_locations = {
            self.FILETYPE_WAD  : self.settings['zandronum']['directories']['wad_directory'],
            self.FILETYPE_IWAD : self.settings['zandronum']['directories']['iwad_directory'],
            self.FILETYPE_CFG  : self.settings['zandronum']['directories']['cfg_directory']
        }
        # Check if a logfile is present and create one if not
        if not os.path.isfile("logfile.txt"):
            open("logfile.txt", 'w+')
            log(LEVEL_OK, "Created logfile.txt")
        # Check to see if our directories exist, and create them if not
        for logfile, location in self.settings['zandronum']['directories'].items():
            if not os.path.exists(location):
                log(LEVEL_STATUS, "{} does not exist, creating it...".format(logfile))
                try:
                    os.makedirs(location)
                except OSError:
                    log(LEVEL_CRITICAL, "Couldn't create {} , quitting.".format(logfile))
                    sys.exit(1)
            else:
                log(LEVEL_OK, "{} exists.".format(logfile))
        # Check to see if mysql database settings are correct
        self.db = mysql.MySQL(self)
        try:
            self.db.connect()
        except mysql.pymysql.MySQLError as e:
            log(LEVEL_ERROR, "MySQL configuration error: {}".format(e))
            sys.exit(1)
        log(LEVEL_OK, "MySQL connection succeeded!")
        # Set up our threaded server monitor
        if platform.system() == "Linux":
            self.monitor = doom.servermonitor.ServerMonitor(self)
            self.monitor_thread = threading.Thread(target=self.monitor.monitor_servers)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
        else:
            log(LEVEL_WARNING, "Server monitoring not supported on {}".format(platform.system()))
        # Attempt to start our TCP server
        self.tcp_listener = tcplistener.TCPListener(self, self.settings['network']['hostname'],
                                                self.settings['network']['port'],
                                                self.settings['network']['secret'])
        atexit.register(_cleanup, self)
        self.tcp_listener.serve()

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

    def check_valid_file(self, type, extension):
        try:
            type = int(type)
        except ValueError:
            return (False, "Invalid type sent.")
        if type not in self.allowed_extensions:
            return (False, "Invalid filetype sent.")
        if extension not in self.allowed_extensions[type]:
            return (False, "{} extensions are not allowed for that type of file.".format(extension))
        return (True, self.filetype_locations[type])

    # Generate a random 32 character hex string
    def generate_unique_id(self):
        return uuid.uuid4().hex

    def check_file_exists(self, potential_file):
        if extension in self.allowed_extensions[self.FILETYPE_WAD]:
            return check_wad_exists(potential_file)
        if extension in self.allowed_extensions[self.FILETYPE_IWAD]:
            return check_iwad_exists(potential_file)
        if extension in self.allowed_extensions[self.FILETYPE_CFG]:
            return check_config_exists(potential_file)

    def check_wad_exists(self, potential_file):
        return True if os.path.isfile(self.settings['zandronum']['directories']['wad_directory'] + potential_file) else False

    def check_iwad_exists(self, potential_file):
        return True if os.path.isfile(self.settings['zandronum']['directories']['iwad_directory'] + potential_file) else False

    def check_config_exists(self, potential_file):
        return True if os.path.isfile(self.settings['zandronum']['directories']['cfg_directory'] + potential_file) else False


# Shutdown hook
def _cleanup(doomhost):
    log(LEVEL_STATUS, "Cleaning up...")
    doomhost.tcp_listener.socket.close()
    doomhost.working = False
    for server in doomhost.servers:
        server.process.kill_server()

def main(args):
    host =  DoomHost()

if __name__ == '__main__':
    main(sys.argv)
