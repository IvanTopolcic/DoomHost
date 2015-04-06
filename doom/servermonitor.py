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

import psutil
from time import sleep
from output.printlogger import *

# This class is responsible for checking the resource usage of servers as well as
# shutting down any which go over the limit
class ServerMonitor():

    def __init__(self, doomhost):
        self.doomhost = doomhost

    def monitor_servers(self):
        log(LEVEL_OK, "Server monitor running.")
        while self.doomhost.working:
            for server in self.doomhost.servers:
                if server.status is not server.SERVER_STARTING and server.status is not server.SERVER_CLOSED:
                    print(server.process.psutil_process.cpu_times())
            sleep(1)
