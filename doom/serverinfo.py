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
#   ServerInfoParseException: Any unusual exceptions from either PHP compression,
#                             or invalid user values. The reason will be attached
#                             to the error message.
#
#   Exception: Anything else if the string is corrupt when JSON tries to parse the
#              string.
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
        self.config = self.get_json_value(str, 'config', None)
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
        self.maxclients = self.get_json_value(int, 'maxclients', 32)
        self.maxplayers = self.get_json_value(int, 'maxplayers', 32)
        self.maxlives = self.get_json_value(int, 'maxlives', 0)
        self.suddendeath = self.get_json_value(bool, 'suddendeath', False)
        self.password = self.get_json_value(str, 'password', None) # Connect password
        self.joinpassword = self.get_json_value(str, 'joinpassword', None)
        # If the default skill is not present, then for coop/survival/invasion should default to skill 3 (UV)
        if 'gamemode' not in self.json_data and self.gamemode in GAMEMODE_COOP_TYPES:
            self.skill = 3

    # A more readable method for assigning default values if it's not in the json data.
    # This is not intended for external usage outside of the class.
    # Throws an exception if the type is incorrect.
    def get_json_value(self, var_type, field_name, default_val):
        if field_name in self.json_data:
            if not isinstance(self.json_data[field_name], var_type):
                raise ServerInfoParseException('Expected json value type translation: ' + var_type)
        return self.json_data[field_name] if field_name in self.json_data else default_val

    # If this server should auto restart
    def should_autorestart(self):
        return self.autorestart

    # Creates the command line string.
    #
    # config_data:
    #   The JSON config data.
    def get_host_command(self, config_data):
        host_str = '' if sys.platform.startswith('win') else './' # Allows Linux/Windows support
        host_str += config_data['zandronum']['executable']
        if config_data['zandronum']['use_host_param']:
            host_str += ' -host'
        host_str += ' +sv_hostname "' + config_data['zandronum']['host_name'] + self.hostname + '"'
        host_str += ' -iwad ' + config_data['zandronum']['iwad_directory'] + self.iwad
        # If the data is on, append the two wads to the wad list at the beginning as a workaround
        if self.data:
            self.wads.insert(0, config_data['zandronum']['skulltag_data_file'])
            self.wads.insert(0, config_data['zandronum']['skulltag_actors_file']) # This is 2nd because we want it prepended to the very front
        # If textcolors is on, append it to the end of the wads list
        if self.textcolors:
            self.wads.append(config_data['zandronum']['textcolours_file'])
        # We need some hacky stuff to combine iwads/pwads sadly (for now)
        if len(self.wads) > 0 or len(self.extraiwads) > 0:
            host_str += ' -file'
            if len(self.extraiwads) > 0:
                for iwadfile in self.extraiwads:
                    host_str += ' ' + config_data['zandronum']['iwad_directory'] + iwadfile + ','
            if len(self.wads) > 0:
                for wadfile in self.wads:
                    host_str += ' ' + config_data['zandronum']['wad_directory'] + wadfile + ','
            host_str = host_str[:-1] # Since we added wads, we have a trailing comma that must be removed
        host_str += self.gamemode + ' 1'
        host_str += ' -skill ' + str(self.skill)
        if self.config is not None:
            host_str += ' +exec "' + config_data['zandronum']['cfg_directory'] + self.config + '"'
        if self.dmflags > 0:
            host_str += ' +dmflags ' + str(self.dmflags)
        if self.dmflags2 > 0:
            host_str += ' +dmflags2 ' + str(self.dmflags2)
        if self.dmflags3 > 0:
            host_str += ' +dmflags3 ' + str(self.dmflags3)
        if self.zadmflags > 0:
            host_str += ' +zadmflags ' + str(self.zadmflags)
        if self.compatflags > 0:
            host_str += ' +compatflags ' + str(self.compatflags)
        if self.compatflags2 > 0:
            host_str += ' +compatflags2 ' + str(self.compatflags2)
        if self.zacompatflags > 0:
            host_str += ' +zacompatflags ' + str(self.zacompatflags)
        if self.instagib:
            host_str += ' +instagib 1'
        if self.buckshot:
            host_str += ' +buckshot 1'
        if self.fraglimit > 0:
            host_str += ' +fraglimit ' + str(self.fraglimit)
        if self.pointlimit > 0:
            host_str += ' +pointlimit ' + str(self.pointlimit)
        if self.duellimit > 0:
            host_str += ' +duellimit ' + str(self.duellimit)
        if self.timelimit > 0:
            host_str += ' +timelimit ' + str(self.timelimit)
        host_str += ' +sv_maxclients ' + str(self.maxclients)
        host_str += ' +sv_maxplayers ' + str(self.maxplayers)
        if self.maxlives > 0:
            host_str += ' +sv_lives ' + str(self.maxlives)
        host_str += ' +sv_suddendeath ' + ('true' if self.suddendeath else 'false')
        if self.password is not None:
            host_str += ' +sv_forcepassword true +sv_password "' + self.password + '"'
        if self.joinpassword is not None:
            host_str += ' +sv_forcejoinpassword true +sv_joinpassword "' + self.joinpassword + '"'
        return host_str


# A custom exception class for any parsing errors.
class ServerInfoParseException(Exception):
    pass
