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
from doom import serverprocess
import threading


# A list of all the critical fields that must be in the json file
REQUIRED_JSON_HOST_FIELDS = ('hostname', 'iwad', 'gamemode')

# A list of gamemodes that should not use nightmare unless the user specifically wants it
GAMEMODE_COOP_TYPES = ['cooperative', 'survival', 'invasion']

# A list of every gamemode type, which means any type should match up with this
ALL_GAMEMODE_TYPES = ['deathmatch', 'cooperative', 'teamplay', 'terminator', 'possession',
                      'teampossession', 'lastmanstanding', 'ctf', 'oneflagctf', 'skulltag', 'duel',
                      'teamgame', 'domination', 'survival', 'invasion']

# A list of every command that should be added to the server start parameters
SERVER_HOST_FIELDS = ['hostname', 'iwad', 'gamemode', 'wads', 'extraiwads', 'skill', 'config',
                      'autorestart', 'dmflags', 'dmflags2', 'dmflags3', 'compatflags', 'compatflags2', 'zadmflags',
                      'zacompatflags', 'instagib', 'buckshot', 'textcolors', 'fraglimit', 'pointlimit', 'duellimit',
                      'maxclients', 'maxplayers', 'maxlives', 'suddendeath', 'password', 'joinpassword']


# Contains server information and populates the values based on what data is
# passed to it from the constructor. When the data is compiled on PHP's end
# into a string, this will be read and should be the constructor's argument.
# Upon reading the json string data, all the fields for creating a server can
# be extracted from the fields.
# Upon processing, the method 'get_host_command' will return the
# command to be run from the command line.
#
# json_string:
#   The string from the PHP encoded server message.
#
# THROWS:
#   ServerInfoParseException: Any unusual exceptions from either PHP compression,
#                             or invalid user values. The reason will be attached
#                             to the error message.
#
#   Exception: Anything else if the string is corrupt when JSON tries to parse the
#              string.

class DoomServer:

    # Server status
    SERVER_STARTING = 0
    SERVER_RUNNING = 1
    SERVER_CLOSED = 2

    def __init__(self, json_data, doomhost):
        self.doomhost = doomhost
        self.owner = "Jenova"
        self.port = doomhost.get_first_free_port()
        self.parameters = []
        self.status = self.SERVER_STARTING
        self.json_data = json_data
        self.hostname = self.json_data['hostname']
        self.iwad = self.json_data['iwad']
        self.gamemode = self.json_data['gamemode']
        if self.gamemode not in ALL_GAMEMODE_TYPES:
            # Silently set the default gamemode type
            self.gamemode = "coop"
        # These fields are optional and will turn to default values if not specified
        self.wads = self.get_host_value(list, 'wads', [])
        self.extraiwads = self.get_host_value(list, 'extraiwads', []) # For the people who want to load two iwads
        self.skill = self.get_host_value(int, 'skill', 4)
        self.data = self.get_host_value(bool, 'data', False)
        self.config = self.get_host_value(str, 'config', None)
        self.autorestart = self.get_host_value(bool, 'autorestart', False)
        self.dmflags = self.get_host_value(int, 'dmflags', 0)
        self.dmflags2 = self.get_host_value(int, 'dmflags2', 0)
        self.dmflags3 = self.get_host_value(int, 'dmflags3', 0)
        self.compatflags = self.get_host_value(int, 'compatflags', 0)
        self.compatflags2 = self.get_host_value(int, 'compatflags2', 0)
        self.zadmflags = self.get_host_value(int, 'zadmflags', 0)
        self.zacompatflags = self.get_host_value(int, 'zacompatflags', 0)
        self.instagib = self.get_host_value(bool, 'instagib', False)
        self.buckshot = self.get_host_value(bool, 'buckshot', False)
        self.textcolors = self.get_host_value(bool, 'textcolors', True)
        self.fraglimit = self.get_host_value(int, 'fraglimit', 0)
        self.pointlimit = self.get_host_value(int, 'pointlimit', 0)
        self.duellimit = self.get_host_value(int, 'duellimit', 0)
        self.timelimit = self.get_host_value(int, 'timelimit', 0)
        self.maxclients = self.get_host_value(int, 'maxclients', 32)
        self.maxplayers = self.get_host_value(int, 'maxplayers', 32)
        self.maxlives = self.get_host_value(int, 'maxlives', 0)
        self.suddendeath = self.get_host_value(bool, 'suddendeath', False)
        self.password = self.get_host_value(str, 'password', None) # Connect password
        self.joinpassword = self.get_host_value(str, 'joinpassword', None)
        # If the default skill is not present, then for coop/survival/invasion should default to skill 3 (UV)
        if 'skill' not in self.json_data and self.gamemode in GAMEMODE_COOP_TYPES:
            self.skill = 3
        self.host_parameters = [doomhost.settings['zandronum']['executable'], '-host']
        self.host_command = self.get_host_command()
        self.process = serverprocess.ServerProcess(self)
        self.doomhost.add_server(self)
        thread = threading.Thread(target=self.process.start_server)
        thread.start()

    # A more readable method for assigning default values if it's not in the json data.
    # This is not intended for external usage outside of the class.
    # If a value is incorrect, it will silently use the default value
    def get_host_value(self, var_type, field_name, default_val):
        if field_name in self.json_data:
            if not isinstance(self.json_data[field_name], var_type):
                # Silently return the default value
                return default_val
        return self.json_data[field_name] if field_name in self.json_data else default_val

    # If this server should auto restart
    def should_autorestart(self):
        return self.autorestart

    # Creates the command line list
    def get_host_command(self):
        host_commands = []
        host_commands.append(self.doomhost.settings['zandronum']['executable'])
        host_commands.append('-host')
        host_commands.append('-port')
        host_commands.append(str(self.doomhost.get_first_free_port()))
        host_commands.append('+sv_hostname')
        host_commands.append(self.doomhost.settings['zandronum']['host_name'] + self.hostname)
        host_commands.append('-iwad')
        host_commands.append(self.doomhost.settings['zandronum']['directories']['iwad_directory'] + self.iwad)
        # If the data is on, append the two wads to the wad list at the beginning as a workaround
        if self.data:
            self.wads.insert(0, self.doomhost.settings['zandronum']['skulltag_data_file'])
            self.wads.insert(0, self.doomhost.settings['zandronum']['skulltag_actors_file'])
        # If textcolors is on, append it to the end of the wads list
        # if self.textcolors:
        #    self.wads.append(self.doomhost.settings['zandronum']['textcolours_file'])
        # We need some hacky stuff to combine iwads/pwads sadly (for now)
        if len(self.wads) > 0 or len(self.extraiwads) > 0:
            if len(self.extraiwads) > 0:
                for iwadfile in self.extraiwads:
                    host_commands.append('-file')
                    host_commands.append(self.doomhost.settings['zandronum']['directories']['iwad_directory'] + iwadfile)
            if len(self.wads) > 0:
                for wadfile in self.wads:
                    host_commands.append('-file')
                    host_commands.append(self.doomhost.settings['zandronum']['directories']['wad_directory'] + wadfile)
        host_commands.append(self.gamemode)
        host_commands.append('true')
        host_commands.append('-skill')
        host_commands.append(str(self.skill))
        if self.config is not None:
            host_commands.append('+exec')
            host_commands.append(self.doomhost.settings['zandronum']['directories']['cfg_directory'] + self.config)
        if self.dmflags > 0:
            host_commands.append('+dmflags')
            host_commands.append(str(self.dmflags))
        if self.dmflags2 > 0:
            host_commands.append('+dmflags2')
            host_commands.append(str(self.dmflags2))
        if self.zadmflags > 0:
            host_commands.append('+zadmflags')
            host_commands.append(str(self.zadmflags))
        if self.compatflags > 0:
            host_commands.append('+compatflags')
            host_commands.append(str(self.compatflags))
        if self.zacompatflags > 0:
            host_commands.append('+zacompatflags')
            host_commands.append(str(self.zacompatflags))
        if self.instagib:
            host_commands.append('+instagib')
            host_commands.append('true')
        if self.buckshot:
            host_commands.append('+buckshot')
            host_commands.append('true')
        if self.fraglimit > 0:
            host_commands.append('+fraglimit')
            host_commands.append(str(self.fraglimit))
        if self.pointlimit > 0:
            host_commands.append('+pointlimit')
            host_commands.append(str(self.pointlimit))
        if self.duellimit > 0:
            host_commands.append('+duellimit')
            host_commands.append(str(self.duellimit))
        if self.timelimit > 0:
            host_commands.append('+timelimit')
            host_commands.append(str(self.timelimit))
        host_commands.append('+sv_maxclients')
        host_commands.append(str(self.maxclients))
        host_commands.append('+sv_maxplayers')
        host_commands.append(str(self.maxplayers))
        if self.maxlives > 0:
            host_commands.append('+sv_maxlives')
            host_commands.append(str(self.maxlives))
        host_commands.append('+sv_suddendeath')
        host_commands.append('true' if self.suddendeath else 'false')
        if self.password is not None:
            host_commands.append('+sv_forcepassword')
            host_commands.append('true')
            host_commands.append('+sv_password')
            host_commands.append(str(self.password))
        if self.joinpassword is not None:
            host_commands.append('+sv_forcejoinpassword')
            host_commands.append('true')
            host_commands.append('+sv_joinpassword')
            host_commands.append(str(self.joinpassword))
        return host_commands


# Checks to see if a server has passed all checks
def is_valid_server(data):
    if not has_required_fields(data):
        return False
    return True


# Checks if the submitted data is fit for server creation
def has_required_fields(data):
    if all(k in data for k in REQUIRED_JSON_HOST_FIELDS):
        return True
    return False

# A custom exception class for any parsing errors.
class ServerInfoParseException(Exception):
    pass
