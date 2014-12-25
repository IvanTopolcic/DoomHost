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


import socket
import struct
import net.huffman
from net.bytebuffer import ByteBuffer, ByteBufferException


LAUNCHER_CHALLENGE = 199

SQF_NAME = 0x00000001
SQF_URL = 0x00000002
SQF_EMAIL = 0x00000004
SQF_MAPNAME = 0x00000008
SQF_MAXCLIENTS = 0x00000010
SQF_MAXPLAYERS = 0x00000020
SQF_PWADS = 0x00000040
SQF_GAMETYPE = 0x00000080
SQF_GAMENAME = 0x00000100
SQF_IWAD = 0x00000200
SQF_FORCEPASSWORD = 0x00000400
SQF_FORCEJOINPASSWORD = 0x00000800
SQF_GAMESKILL = 0x00001000
SQF_BOTSKILL = 0x00002000
SQF_DMFLAGS = 0x00004000 # Deprecated don't use
SQF_LIMITS = 0x00010000
SQF_TEAMDAMAGE = 0x00020000
SQF_TEAMSCORES = 0x00040000 # Deprecated don't use
SQF_NUMPLAYERS = 0x00080000
SQF_PLAYERDATA = 0x00100000
SQF_TEAMINFO_NUMBER = 0x00200000
SQF_TEAMINFO_NAME = 0x00400000
SQF_TEAMINFO_COLOR = 0x00800000
SQF_TEAMINFO_SCORE = 0x01000000
SQF_TESTING_SERVER = 0x02000000
SQF_DATA_MD5SUM = 0x04000000
SQF_ALL_DMFLAGS = 0x08000000
SQF_SECURITY_SETTINGS = 0x10000000

# The information we want from a server
SQF_DESIRED_FLAGS = SQF_MAPNAME | SQF_MAXCLIENTS | SQF_MAXPLAYERS | SQF_PWADS | SQF_GAMETYPE | SQF_GAMENAME | \
                    SQF_IWAD | SQF_GAMESKILL | SQF_BOTSKILL | SQF_LIMITS | SQF_TEAMDAMAGE | SQF_ALL_DMFLAGS

# The gamemode enumeration
GAMEMODE_COOPERATIVE = 0
GAMEMODE_SURVIVAL = 1
GAMEMODE_INVASION = 2
GAMEMODE_DEATHMATCH = 3
GAMEMODE_TEAMPLAY = 4
GAMEMODE_DUEL = 5
GAMEMODE_TERMINATOR = 6
GAMEMODE_LASTMANSTANDING = 7
GAMEMODE_TEAMLMS = 8
GAMEMODE_POSSESSION = 9
GAMEMODE_TEAMPOSSESSION = 10
GAMEMODE_TEAMGAME = 11
GAMEMODE_CTF = 12
GAMEMODE_ONEFLAGCTF = 13
GAMEMODE_SKULLTAG = 14
GAMEMODE_DOMINATION = 15

# A quick lookup for names
GAMEMODE_STRING = ["COOPERATIVE", "SURVIVAL", "INVASION", "DEATHMATCH", "TEAMPLAY",
                     "DUEL", "TERMINATOR", "LASTMANSTANDING", "TEAMLMS", "POSSESSION",
                     "TEAMPOSSESSION", "TEAMGAME", "CTF", "ONEFLAGCTF", "SKULLTAG",
                     "DOMINATION"]


# Performs a server query by asking for the information
def perform_server_query(ip, port):
    querybytes = struct.pack("<LLL", LAUNCHER_CHALLENGE, SQF_DESIRED_FLAGS, 0)  # Last param isn't needed
    encodeddata = net.huffman.encode(querybytes)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            # Set socket options
            s.setblocking(True)
            s.settimeout(5.0)

            # Send out the encoded data, and wait for the response
            s.sendto(encodeddata, (ip, port))
            data, address = s.recvfrom(2048)  # This should be big enough to hold the information...
            decodeddata = net.huffman.decode(data)
            bb = ByteBuffer(True)
            bb.put_bytes(decodeddata)
            print("Decoded data length =", len(decodeddata))
            print(decodeddata)

            # Go through the elements now, starting with the header
            firstheader = bb.get_int()
            if firstheader != 5660023:  # If it's not this number, we're flooding or banned
                return False

            # Discard the time, we don't care
            bb.get_int()

            # Get the custom version string
            versionstring = bb.get_string_null_terminated()
            print("Version:", versionstring)

            # Check what fields we're sent back
            bitflags = bb.get_int()
            print("Bit flags:", bitflags)
            if bitflags & SQF_NAME:
                servername = bb.get_string_null_terminated()
                print("Server name:", servername)
            if bitflags & SQF_URL:
                url = bb.get_string_null_terminated()
                print("URL:", url)
            if bitflags & SQF_EMAIL:
                email = bb.get_string_null_terminated()
                print("Email:", email)
            if bitflags & SQF_MAPNAME:
                mapname = bb.get_string_null_terminated()
                print("Map name:", mapname)
            if bitflags & SQF_MAXCLIENTS:
                maxclients = bb.get_byte()
                print("Max clients:", maxclients)
            if bitflags & SQF_MAXPLAYERS:
                maxplayers = bb.get_byte()
                print("Max players:", maxplayers)
            if bitflags & SQF_PWADS:
                numpwads = bb.get_byte()
                pwadlist = []
                for i in range(numpwads):
                    pwadlist.append(bb.get_string_null_terminated())
                print("Pwads:", pwadlist)
            if bitflags & SQF_GAMETYPE:
                gamemode = bb.get_byte()
                is_instagib = bb.get_byte() > 0
                is_buckshot = bb.get_byte() > 0
                print("Gamemode is", GAMEMODE_STRING[gamemode], ", Instagib:", is_instagib, ", Buckshot:", is_buckshot)
            if bitflags & SQF_GAMENAME:
                gamename = bb.get_string_null_terminated()
                print("Game name:", gamename)
            if bitflags & SQF_IWAD:
                iwad = bb.get_string_null_terminated()
                print("Iwad:", iwad)
            if bitflags & SQF_FORCEPASSWORD:
                is_force_password = bb.get_byte() > 0
                print("Force pass:", is_force_password)
            if bitflags & SQF_FORCEJOINPASSWORD:
                is_force_join_password = bb.get_byte() > 0
                print("Force join pass:", is_force_join_password)
            if bitflags & SQF_GAMESKILL:
                gameskill = bb.get_byte()
                print("Game skill level:", gameskill)
            if bitflags & SQF_BOTSKILL:
                botskill = bb.get_byte()
                print("Bot skill level:", botskill)
            if bitflags & SQF_DMFLAGS:
                old_dmflags = bb.get_int()
                old_dmflags2 = bb.get_int()
                old_compatflags = bb.get_int()
                print("WARNING: Got deprecated flag SQF_DMFLAGS")
            if bitflags & SQF_LIMITS:
                fraglimit = bb.get_short_unsigned()
                timelimit = bb.get_short_unsigned()
                if timelimit > 0:
                    time_left_mins = bb.get_short_unsigned()  # Apparently this is only sent if the time limit > 0
                    print("TimeLeftMinutes =", time_left_mins)
                duellimit = bb.get_short_unsigned()
                pointlimit = bb.get_short_unsigned()
                winlimit = bb.get_short_unsigned()
                print("Limits: Frags =", fraglimit, ", Timelimit =", timelimit, ", Duellimit =", duellimit,
                      ", Pointlimit =", pointlimit, ", Winlimit =", winlimit)
            if bitflags & SQF_TEAMDAMAGE:
                teamdamagefactor = bb.get_float()
                print("Team damage factor:", teamdamagefactor)
            if bitflags & SQF_TEAMSCORES:
                teamscore_red = bb.get_short()
                teamscore_blue = bb.get_short()
                print("WARNING: Got deprecated flag SQF_TEAMSCORES, this may not even be parsed right")
            if bitflags & SQF_NUMPLAYERS:
                numplayers = bb.get_byte()
                print("Number of players:", numplayers)
            if bitflags & SQF_PLAYERDATA:
                print("Player data for ", numplayers, " players:")
                for p in range(numplayers):  # The server SHOULD send us SQF_NUMPLAYERS previously or else Zan is bugged
                    player_name = bb.get_string_null_terminated()
                    player_scorecount = bb.get_short()
                    player_ping = bb.get_short()
                    player_is_spec = bb.get_byte() > 0
                    player_is_bot = bb.get_byte() > 0
                    player_team = bb.get_byte()
                    player_time_minutes = bb.get_byte()
                    print("\tPlayer", player_name, ": points =", player_scorecount, ", ping =", player_ping,
                          ", is spec =", player_is_spec, ", is bot = ", player_is_bot, ", team =", player_team,
                          ", time in server (minutes) =", player_time_minutes)
            if bitflags & SQF_TEAMINFO_NUMBER:
                numteams = bb.get_byte()
                print("Number of teams:", numteams)
            if bitflags & SQF_TEAMINFO_NAME or bitflags & SQF_TEAMINFO_COLOR or bitflags & SQF_TEAMINFO_SCORE:
                for i in range(numteams):
                    if bitflags & SQF_TEAMINFO_NAME:
                        team_name = bb.get_string_null_terminated()
                        print(i, " team's name:", team_name)
                    if bitflags & SQF_TEAMINFO_COLOR:
                        team_color = bb.get_int()
                        print(i, " team's color:", team_color)
                    if bitflags & SQF_TEAMINFO_SCORE:
                        team_score = bb.get_short()
                        print(i, " team's score:", team_score)
            if bitflags & SQF_TESTING_SERVER:
                is_running_custom = bb.get_byte() > 0
                custom_binary_name = bb.get_string_null_terminated()
                print("Running custom =", is_running_custom, "[", custom_binary_name, "]")
            if bitflags & SQF_DATA_MD5SUM:
                data_md5_sum = bb.get_string_null_terminated()
                print("MD5 sum:", data_md5_sum)
            if bitflags & SQF_ALL_DMFLAGS:
                num_dm_flags = bb.get_byte()
                dmflaglist = [0, 0, 0, 0, 0]  # DMFlags, DMFlags2, DMFlags3/ZaDMFlags, CompatFlags, CompatFlags2/ZaComp
                for flagindex in range(num_dm_flags):
                    dmflaglist[flagindex] = bb.get_int()
                print("DMFlag/CompatFlag list:", dmflaglist)
            if bitflags & SQF_SECURITY_SETTINGS:
                is_security_set = bb.get_byte() > 0
                print("Security set:", is_security_set)
            print("Done reading, left over bytes =", bb.size())
        except socket.timeout:
            print("Timeout when trying to perform a server query to", ip, port)
            return False
        except ByteBufferException as e:
            print("ByteBuffer extraction failed:", e)
            return False
    return True
