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

from colorama import init, Fore, Style
from datetime import datetime

# Status should be used for notifying the user of events that are expected, a received packet for example
LEVEL_STATUS = 0

# Warning should be used for notifying the user of a non-fatal error, such as an unknown packet
LEVEL_WARNING = 1

# Errors should be used for notifying the user of a fatal error, such as a missing configuration file
LEVEL_ERROR = 2

# Ok should be used for notifying the user of things that worked (loaded configuration, database connection established)
LEVEL_OK = 3

# Our logfile
LOGFILE = "logfile.txt"


# Neatly prints output to the console
def write_console(level, line):
    if level == LEVEL_STATUS:
        print('[ Status ] ' + line)
    elif level == LEVEL_WARNING:
        print('[ ' + Fore.YELLOW + 'Warning' + Fore.RESET + ' ] ' + line)
    elif level == LEVEL_ERROR:
        print('[ ' + Fore.RED + 'Error' + Fore.RESET + ' ] ' + line)
    elif level == LEVEL_OK:
        print('[ ' + Fore.GREEN + 'Ok' + Fore.RESET + ' ] ' + line)

# Logs the message to our logfile
def write_logfile(level, line):
    f = open('logfile.txt', 'a')
    f.write(datetime.now().isoformat() + ' - ')
    if level == LEVEL_STATUS:
        f.write('[ Status ] ' + line)
    elif level == LEVEL_WARNING:
        f.write('[ Warning ] ' + line)
    elif level == LEVEL_ERROR:
        f.write('[ Error ] ' + line)
    elif level == LEVEL_OK:
        f.write('[ Ok ] ' + line)
    f.write('\n')
    f.close()

# Logs and prints
def log(level, line):
    write_console(level, line)
    write_logfile(level, line)
