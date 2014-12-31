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

# Starts a process from the command list
# command_list:
#   The commands to use, example: ['zandronum', '-host', 'cooperative 1']
def start_server(command_list):
    return subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

# NOTE: Idea inspired from: http://stackoverflow.com/questions/5173945/python-monitoring-stderr-and-stdout-of-a-subprocess
def read_stdout_until_end(proc):
    while proc.poll() is None:
        line = proc.stdout.readline()
        if line:
            print(line) # TODO - Put reasonable stuff here later