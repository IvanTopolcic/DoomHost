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


class ServerProcess():
    def __init__(self, host_command):
        self.process = None
        self.host_command = host_command

    # Starts a process from the command list
    # command_list:
    #   The commands to use, example: ['zandronum', '-host', 'cooperative 1']
    def start_server(self):
        self.process = psutil.Popen(self.host_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
