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
import socket
import time
import struct
from doom import doomserver
from output.printlogger import *


# Listens for incoming messages and performs appropriate actions
class TCPListener():

    # Our reply status
    STATUS_ERROR = 0
    STATUS_OK = 1

    # Uploaded file types
    FILETYPE_WAD = 0
    FILETYPE_IWAD = 1
    FILETYPE_CFG = 2

    # Required fields for specified actions
    # The listener will error out if these are not present
    # NOTE: This does not validate the values, but only shows if they are present
    required_fields = {
        'general': ['username', 'password'],
        'host':    ['hostname', 'iwad', 'gamemode'],
        'kill':    ['port'],
        'upload':  ['name', 'type']
    }

    def __init__(self, doomhost, hostname, port, secret):
        self.doomhost = doomhost
        self._hostname = hostname
        self._port = port
        self._secret = secret
        self._blacklist = []
        # Since our listener isn't threaded, this should be more convenient
        self.connection = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Checks to make sure an action has all the data that it needs
    def check_required_fields(self, action, array_data):
        for field in self.required_fields[action]:
            if field not in array_data:
                log(LEVEL_WARNING, "Missing {} from JSON data.".format(field))
                self.reply(self.STATUS_ERROR, "Looks like not all information was filled out. Please fill out {}".format(field))
                return False
        return True

    # Sends a reply to the client
    def reply(self, status, message):
        self.connection.send(bytes("{'status': " + str(status) + ", 'reply': '" + message + "'}", encoding='UTF-8'))

    # Check if an IP address is banned
    def is_banned(self, address):
        for i, (hostname, unbantime) in enumerate(self._blacklist):
            if hostname == address:
                if unbantime < int(time.time()):
                    del self._blacklist[i]
                    log(LEVEL_STATUS, "Ban on {} expired.".format(hostname))
                    return False
                else:
                    return True
        return False

    # Scans the packet received for our JSON string and returns a tuple containing the JSON string and the rest of the packet
    def extract_string(self, bytes):
        length = struct.unpack('h', bytes[:2])[0]
        return (bytes[2:length+2].decode('utf-8'), bytes[length+2:len(bytes)])

    def process_upload_packet(self, data, address):
        if not self.check_required_fields('upload', data):
            return
        if self.doomhost.check_wad_exists(data['name']):
            log(LEVEL_STATUS, "Tried to upload file ({}) that already exists.".format(data['name']))
            self.reply(self.connection, "That wad already exists!")
            return
        # Create a temporary file that we write to, which we'll move to our final directory later
        f = open(data['name'], 'bw+')
        # Our first packet actually contained some data for the file that we need, write it!
        f.write(rest)
        # Since we're getting a large file, we need to keep listening for more information
        file_data = self.connection.recv(4096)
        while (file_data):
            f.write(file_data)
            file_data = self.connection.recv(4096)
        f.close()

    def process_host_packet(self, data, address):
        log(LEVEL_STATUS, "Processing host action from {}".format(address))
        if not self.check_required_fields('host', data):
            return
        if self.doomhost.get_first_free_port() is None:
            self.reply(self.STATUS_ERROR, "The global server limit has been reached.")
            log(LEVEL_WARNING, "The global server limit has been reached.")
            return
        if doomserver.is_valid_server(data):
            doomserver.DoomServer(data, self.doomhost)
        else:
            log(LEVEL_WARNING, "Received server host request without all information, ignoring...")

    def process_kill_packet(self, data, address):
        log(LEVEL_STATUS, "Processing kill action from {}".format(address))
        if not self.check_required_fields('kill', data):
            return
        if not self.doomhost.is_valid_port(data['port']):
            log(LEVEL_WARNING, "Invalid port sent from {}".format(address))
            self.reply(self.STATUS_ERROR, "Invalid port.")
            return
        server = self.doomhost.get_server(data['port'])
        if server is not None:
            if server.status is not server.SERVER_STARTING:
                server.process.kill_server()
                self.reply(self.STATUS_OK, "Killed server.")
            else:
                log(LEVEL_STATUS, "Not killing a server that hasn't started yet.")
                self.reply(self.STATUS_ERROR, "Server must load up before being killed.")
        else:
            log(LEVEL_STATUS, "Can't find server running on port {} to kill".format(data['port']))
            self.reply(self.STATUS_ERROR, "Server running on port {} does not exist.".format(data['port']))

    # Main listener function
    def serve(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self._hostname, self._port))
        self.socket.listen(True)
        log(LEVEL_OK, "Listening on {}:{}".format(self._hostname, self._port))
        while True:
            self.connection, address = self.socket.accept()
            if self.is_banned(address[0]):
                log(LEVEL_STATUS, "Banned IP {} connecting, ignoring request.".format(address[0]))
                self.reply(self.STATUS_ERROR, "Your IP address is banned.")
                continue
            packet = self.connection.recv(4096)
            try:
                data = json.loads(self.extract_string(packet)[0])
                rest = self.extract_string(packet)[1]
            except ValueError as e:
                log(LEVEL_WARNING, "Received incorrectly formatted JSON string {} from {}".format(self.extract_string(packet)[0], address[0]))
                self.reply(self.STATUS_ERROR, "Looks like there was an error processing your request. Please try again.")
                self.connection.close()
                continue
            if not data:
                break
            if 'secret' in data:
                if data['secret']:
                    if not self.check_required_fields('general', data):
                        continue
                    if not self.doomhost.db.check_login(data['username'], data['password']):
                        log(LEVEL_WARNING, "Invalid password for {} from {}".format(data['username'], address[0]))
                        self.reply(self.STATUS_ERROR, "Invalid username or password combination.")
                        continue
                    data['user'] = self.doomhost.db.get_user(data['username'])
                    # Process the packet
                    if data['action'] == 'upload':
                        self.process_upload_packet(data, address[0])
                    if data['action'] == 'host':
                        self.process_host_packet(data, address[0])
                    elif data['action'] == 'kill':
                        self.process_kill_packet(data, address[0])
                else:
                    log(LEVEL_WARNING, "Incorrect secret from {}, banning address for 3 seconds.".format(address[0]))
                    self.reply(self.STATUS_ERROR, "Received incorrect secret.")
                    # If not already in our blacklist, ban the IP for 3 seconds
                    banned = False
                    for hostname, bantime in self._blacklist:
                        if hostname == address[0]:
                            banned = True
                    if not banned:
                        self._blacklist.append((address[0], int(time.time()) + 3))
            else:
                log(LEVEL_WARNING, "Didn't receive secret from {}".format(address[0]))
                self.reply(self.STATUS_ERROR, "Please send us the secret!")
        connection.close()

