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
from doom import doomserver
from output import printlogger


class TCPListener():
    def __init__(self, doomhost, hostname, port, secret):
        self.doomhost = doomhost
        self._hostname = hostname
        self._port = port
        self._secret = secret
        self._blacklist = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Check if an IP address is banned
    def is_banned(self, address):
        for i, (hostname, unbantime) in enumerate(self._blacklist):
            if hostname == address:
                if unbantime < int(time.time()):
                    del self._blacklist[i]
                    printlogger.write_console(printlogger.LEVEL_STATUS, "Ban on {} expired.".format(hostname))
                    return False
                else:
                    return True
        return False

    # Main listener function
    def serve(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self._hostname, self._port))
        self.socket.listen(True)
        printlogger.write_console(printlogger.LEVEL_OK, "Listening on {}:{}".format(self._hostname, self._port))
        while True:
            connection, address = self.socket.accept()
            if self.is_banned(address[0]):
                printlogger.write_console(printlogger.LEVEL_STATUS, "Banned IP {} connecting, ignoring request.".format(address[0]))
                connection.send(b"{'status': 0, 'reply':'IP address is banned.'}")
                connection.close()
                continue
            try:
                data = json.loads(connection.recv(2048).decode("UTF-8"))
            except ValueError:
                printlogger.write_console(printlogger.LEVEL_WARNING, "Received incorrectly formatted JSON string from {}".format(address[0]))
                connection.send(b"{'status': 0, 'reply':'Received incorrectly formatted JSON string.'}")
                connection.close()
                continue
            if not data:
                break
            if 'secret' in data:
                if data['secret'] == self._secret:
                    # Process the packet
                    if data['action'] == 'host':
                        if doomserver.is_valid_server(data):
                            doomserver.DoomServer(data, self.doomhost)
                        else:
                            printlogger.write_console(printlogger.LEVEL_WARNING, "Received server host request without all information, ignoring...")
                    connection.close()
                else:
                    printlogger.write_console(printlogger.LEVEL_WARNING, "Incorrect secret from {}, banning address for 3 seconds.".format(address[0]))
                    connection.send(b"{'status': 0, 'reply':'Incorrect secret received.'}")
                    connection.close()
                    # If not already in our blacklist, ban the IP for 3 seconds
                    banned = False
                    for hostname, bantime in self._blacklist:
                        if hostname == address[0]:
                            banned = True
                    if not banned:
                        self._blacklist.append((address[0], int(time.time()) + 3))
