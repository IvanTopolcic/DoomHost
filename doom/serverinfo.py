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


# A list of all the critical fields that must be in the json file
REQUIRED_JSON_HOST_FIELDS = ['hostname', 'iwad', 'gamemode']

# A list of gamemodes that should not use nightmare unless the user specifically wants it
GAMEMODE_COOP_TYPES = ['cooperative', 'survival', 'invasion']

# A list of every gamemode type, which means any type should match up with this
ALL_GAMEMODE_TYPES = ['deathmatch', 'cooperative', 'teamplay', 'terminator', 'possession',
                      'teampossession', 'lastmanstanding', 'ctf', 'oneflagctf', 'skulltag', 'duel',
                      'teamgame', 'domination', 'cooperative', 'survival', 'invasion']


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
#   - ServerInfoParseException: Any unusual exceptions from either PHP compression,
#                               or invalid user values. The reason will be attached
#                               to the error message.
#
#   - Exception: Anything else if the string is corrupt when JSON tries to
#                parse the string.
class ServerInfo:
    def __init__(self, json_string):
        # If it's None, not a String, or something invalid, throw an exception
        if json_string is None:
            raise ServerInfoParseException('Json string passed to ServerInfo is of type None')
        elif type(json_string) != type(str()):
            raise ServerInfoParseException('Json string is not a String')
        elif len(json_string) == 0:
            raise ServerInfoParseException('Passed ServerInfo constructor an empty String')
        self.json_data = json.loads(json_string)
        # These are all the values that are critical
        for field in REQUIRED_JSON_HOST_FIELDS:
            if field not in self.json_data:
                raise ServerInfoParseException('Missing "' + field + '" argument from JSON data')
        self.hostname = self.json_data['hostname']
        self.iwad = self.json_data['iwad']
        self.gamemode = self.json_data['gamemode']
        if self.gamemode not in ALL_GAMEMODE_TYPES:
            raise ServerInfoParseException('Invalid gamemode type: ' + self.gamemode)
        # These fields are optional and will turn to default values if not specified
        self.wads = self.get_json_value(list, 'wads', [])
        self.extraiwads = self.get_json_value(list, 'extraiwads', []) # For the people who want to load two iwads
        self.skill = self.get_json_value(int, 'skill', 4)
        self.data = self.get_json_value(bool, 'data', False)
        self.config = self.get_json_value(str, 'config', '')
        self.autorestart = self.get_json_value(bool, 'autorestart', False)
        self.dmflags = self.get_json_value(int, 'dmflags', 0)
        self.dmflags2 = self.get_json_value(int, 'dmflags2', 0)
        self.dmflags3 = self.get_json_value(int, 'dmflags3', 0)
        self.compatflags = self.get_json_value(int, 'compatflags', 0)
        self.compatflags2 = self.get_json_value(int, 'compatflags2', 0)
        self.zadmflags = self.get_json_value(int, 'zadmflags', 0)
        self.zacompatflags = self.get_json_value(int, 'zacompatflags', 0)
        self.instagib =  self.get_json_value(bool, 'instagib', False)
        self.buckshot =  self.get_json_value(bool, 'buckshot', False)
        self.textcolors = self.get_json_value(bool, 'textcolors', True)
        self.fraglimit = self.get_json_value(int, 'fraglimit', 0)
        self.pointlimit = self.get_json_value(int, 'pointlimit', 0)
        self.duellimit = self.get_json_value(int, 'duellimit', 0)
        self.timelimit = self.get_json_value(int, 'timelimit', 0)
        self.maplist = self.get_json_value(list, 'maplist', [])
        self.usewadmaps = self.get_json_value(bool, 'usewadmaps', True if len(self.maplist) == 0 else False) # Parse maps out of the wad if none are provided?
        self.maxclients = self.get_json_value(int, 'maxclients', 32)
        self.maxplayers = self.get_json_value(int, 'maxplayers', 32)
        self.maxlives = self.get_json_value(int, 'maxlives', 0)
        self.suddendeath = self.get_json_value(bool, 'suddendeath', False)
        self.password = self.get_json_value(str, 'password', None) # Connect password
        self.joinpassword = self.get_json_value(str, 'joinpassword', None)
        # If the default skill is not present, then for coop/survival/invasion should default to skill 3 (UV)
        if 'gamemode' not in self.json_data and self.gamemode not in GAMEMODE_COOP_TYPES:
            self.skill = 3

    # A more readable method for assigning default values if it's not in the json data.
    # This is not intended for external usage outside of the class.
    # Throws an exception if the type is incorrect.
    def get_json_value(self, var_type, field_name, default_val):
        if field_name in self.json_data:
            if not isinstance(self.json_data[field_name], var_type):
                raise ServerInfoParseException('Expected json value type translation: ' + var_type)
        return self.json_data[field_name] if field_name in self.json_data else default_val

    # Creates the command line string.
    #
    #   exe_path:
    #       The full path to the executable's folder (ex: '/home/mypath/'), should end with a slash.
    #   binary_name:
    #       The name of the binary (ex: zandronum-server, or zandronum.exe).
    #   wad_path:
    #       The full directory path to the wads (ex: /home/wads/), should end with a slash.
    #   config_path:
    #       The full directory path to the configs (ex: /home/configs/), should end with a slash.
    #   use_host_arg:
    #       If "-host" should be added to the command line (mainly for windows or a dual client/server binary).
    def get_host_command(self, exe_path, binary_name, iwad_path, wad_path, config_path, use_host_arg = False):
        host_str = '' if sys.platform.startswith('win') else './' # Allows Linux/Windows support
        host_str += exe_path
        host_str += binary_name
        if use_host_arg:
            host_str += ' -host'
        host_str += ' -iwad ' + iwad_path + self.iwad
        # TODO - Left off here
        return host_str


# A custom exception class for any parsing errors.
class ServerInfoParseException(Exception):
    pass
