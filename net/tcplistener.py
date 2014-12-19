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
                    print("Ban on {} expired.".format(hostname))
                    return False
                else:
                    return True
        return False

    # Main listener function
    def serve(self):
        self.socket.bind((self._hostname, self._port))
        self.socket.listen(True)
        print("Listening on {}:{}".format(self._hostname, self._port))
        while True:
            connection, address = self.socket.accept()
            if self.is_banned(address[0]):
                print("Banned IP {} connecting, ignoring request.".format(address[0]))
                connection.send(b"{'status': 0, 'reply':'IP address is banned.'}")
                connection.close()
                continue
            try:
                data = json.loads(connection.recv(2048).decode("UTF-8"))
            except ValueError:
                print("Received incorrectly formatted JSON string from {}".format(address[0]))
                connection.send(b"{'status': 0, 'reply':'Received incorrectly formatted JSON string.'}")
                connection.close()
                continue
            if not data:
                break
            if 'secret' in data:
                if data['secret'] == self._secret:
                    # Process the packet
                    print("This is where the action will be processed (host, kill, etc) TODO")
                    connection.send(b"{'status': 1, 'reply':'Everything looks okay!'}")
                    connection.close()
                    None
                else:
                    print("Incorrect secret from {}, banning address for 3 seconds.".format(address[0]))
                    connection.send(b"{'status': 0, 'reply':'Incorrect secret received.'}")
                    connection.close()
                    # If not already in our blacklist, ban the IP for 3 seconds
                    banned = False
                    for hostname, bantime in self._blacklist:
                        if hostname == address[0]:
                            banned = True
                    if not banned:
                        self._blacklist.append((address[0], int(time.time()) + 3))