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

import subprocess
import psutil
import threading
from output.printlogger import *


class ServerProcess():
    def __init__(self, server):
        self.server = server
        self.psutil_process = None
        self.host_command = server.host_command

    # Starts a process from the command list
    # command_list:
    #   The commands to use, example: ['zandronum', '-host', 'cooperative 1']
    def start_server(self):
        self.psutil_process = psutil.Popen(self.host_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in self.psutil_process.stdout:
            if self.server.status == self.server.SERVER_STARTING:
                if line == "UDP Initialized.\n":
                    self.server.doomhost.db.set_server_online(self.server.unique_id)
                    log(LEVEL_OK, "Server from {} on port {} started successfully.".format(self.server.owner['username'], self.server.port))
                    self.server.status = self.server.SERVER_RUNNING
        # This means our program terminated
        if self.server.status == self.server.SERVER_STARTING:
            self.server.doomhost.tcp_listener.reply(self.server.doomhost.tcp_listener.STATUS_ERROR, "There was a problem starting your server.")
        log(LEVEL_OK, "Server from {} on port {} was stopped.".format(self.server.owner['name'], self.server.port))
        if self.server.status == self.server.SERVER_RUNNING:
            self.server.doomhost.remove_server(self.server)
        self.server.status = self.server.SERVER_CLOSED

    def kill_server(self):
        self.psutil_process.kill()
