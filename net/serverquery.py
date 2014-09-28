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


from misc.enum import enum
import net.huffman
from net.bytebuffer import ByteBuffer, ByteBufferException
import socket
import struct


# The launcher challenge
__launcher_challenge = 199

# Server query flags
__SQF = enum(NAME=0x00000001,
             URL=0x00000002,
             EMAIL=0x00000004,
             MAPNAME=0x00000008,
             MAXCLIENTS=0x00000010,
             MAXPLAYERS=0x00000020,
             PWADS=0x00000040,
             GAMETYPE=0x00000080,
             GAMENAME=0x00000100,
             IWAD=0x00000200,
             FORCEPASSWORD=0x00000400,
             FORCEJOINPASSWORD=0x00000800,
             GAMESKILL=0x00001000,
             BOTSKILL=0x00002000,
             DMFLAGS=0x00004000,  # Deprecated, don't use
             LIMITS=0x00010000,
             TEAMDAMAGE=0x00020000,
             TEAMSCORES=0x00040000,  # Deprecated, don't use
             NUMPLAYERS=0x00080000,
             PLAYERDATA=0x00100000,
             TEAMINFO_NUMBER=0x00200000,
             TEAMINFO_NAME=0x00400000,
             TEAMINFO_COLOR=0x00800000,
             TEAMINFO_SCORE=0x01000000,
             TESTING_SERVER=0x02000000,
             DATA_MD5SUM=0x04000000,
             ALL_DMFLAGS=0x08000000,
             SECURITY_SETTINGS=0x10000000)

# The information we want from a server
__SQF_DESIRED_FLAGS = __SQF.MAPNAME | __SQF.MAXCLIENTS | __SQF.MAXPLAYERS | __SQF.PWADS | __SQF.GAMETYPE | \
    __SQF.GAMENAME | __SQF.IWAD | __SQF.GAMESKILL | __SQF.BOTSKILL | __SQF.LIMITS

# The gamemode enumeration
__GAMEMODE = enum(COOPERATIVE=0, SURVIVAL=1, INVASION=2, DEATHMATCH=3, TEAMPLAY=4,
                  DUEL=5, TERMINATOR=6, LASTMANSTANDING=7, TEAMLMS=8, POSSESSION=9,
                  TEAMPOSSESSION=10, TEAMGAME=11, CTF=12, ONEFLAGCTF=13, SKULLTAG=14,
                  DOMINATION=15)

# A quick lookup for names
__GAMEMODE_STRING = ["COOPERATIVE", "SURVIVAL", "INVASION", "DEATHMATCH", "TEAMPLAY",
                     "DUEL", "TERMINATOR", "LASTMANSTANDING", "TEAMLMS", "POSSESSION",
                     "TEAMPOSSESSION", "TEAMGAME", "CTF", "ONEFLAGCTF", "SKULLTAG",
                     "DOMINATION"]


# Performs a server query by asking for the information
def perform_server_query(ip, port):
    querybytes = struct.pack("<LLL", __launcher_challenge, __SQF_DESIRED_FLAGS, 0)  # Last param isn't needed
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
            if bitflags & __SQF.NAME:
                servername = bb.get_string_null_terminated()
                print("Server name:", servername)
            if bitflags & __SQF.URL:
                url = bb.get_string_null_terminated()
                print("URL:", url)
            if bitflags & __SQF.EMAIL:
                email = bb.get_string_null_terminated()
                print("Email:", email)
            if bitflags & __SQF.MAPNAME:
                mapname = bb.get_string_null_terminated()
                print("Map name:", mapname)
            if bitflags & __SQF.MAXCLIENTS:
                maxclients = bb.get_byte()
                print("Max clients:", maxclients)
            if bitflags & __SQF.MAXPLAYERS:
                maxplayers = bb.get_byte()
                print("Max players:", maxplayers)
            if bitflags & __SQF.PWADS:
                numpwads = bb.get_byte()
                pwadlist = []
                for i in range(numpwads):
                    pwadlist.append(bb.get_string_null_terminated())
                print("Pwads:", pwadlist)
            if bitflags & __SQF.GAMETYPE:
                gamemode = bb.get_byte()
                is_instagib = bb.get_byte() > 0
                is_buckshot = bb.get_byte() > 0
                print("Gamemode is", __GAMEMODE_STRING[gamemode], ", Instagib:", is_instagib, ", Buckshot:", is_buckshot)
            if bitflags & __SQF.GAMENAME:
                gamename = bb.get_string_null_terminated()
                print("Game name:", gamename)
            if bitflags & __SQF.IWAD:
                iwad = bb.get_string_null_terminated()
                print("Iwad:", iwad)
            if bitflags & __SQF.FORCEPASSWORD:
                is_force_password = bb.get_byte() > 0
                print("Force pass:", is_force_password)
            if bitflags & __SQF.FORCEJOINPASSWORD:
                is_force_join_password = bb.get_byte() > 0
                print("Force join pass:", is_force_join_password)
            if bitflags & __SQF.GAMESKILL:
                gameskill = bb.get_byte()
                print("Game skill level:", gameskill)
            if bitflags & __SQF.BOTSKILL:
                botskill = bb.get_byte()
                print("Bot skill level:", botskill)
            if bitflags & __SQF.DMFLAGS:
                old_dmflags = bb.get_int()
                old_dmflags2 = bb.get_int()
                old_compatflags = bb.get_int()
                print("WARNING: Got deprecated flag SQF_DMFLAGS")
            if bitflags & __SQF.LIMITS:
                fraglimit = bb.get_short_unsigned()
                timelimit = bb.get_short_unsigned()
                time_left_mins = bb.get_short_unsigned()
                duellimit = bb.get_short_unsigned()
                pointlimit = bb.get_short_unsigned()
                winlimit = bb.get_short_unsigned()
                print("Limits: Frags =", fraglimit, ", Timelimit =", timelimit, ", TimeLeftMinutes =", time_left_mins,
                      ", Duellimit =", duellimit, ", Pointlimit =", pointlimit, ", Winlimit =", winlimit)
            if bitflags & __SQF.TEAMDAMAGE:
                teamdamagefactor = bb.get_float()
                print("Team damage factor:", teamdamagefactor)
            if bitflags & __SQF.TEAMSCORES:
                teamscore_red = bb.get_short()
                teamscore_blue = bb.get_short()
                print("WARNING: Got deprecated flag SQF_TEAMSCORES, this may not even be parsed right")
            if bitflags & __SQF.NUMPLAYERS:
                numplayers = bb.get_byte()
                print("Number of players:", numplayers)
            if bitflags & __SQF.PLAYERDATA:
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
            if bitflags & __SQF.TEAMINFO_NUMBER:
                numteams = bb.get_byte()
                print("Number of teams:", numteams)
            if bitflags & __SQF.TEAMINFO_NAME or bitflags & __SQF.TEAMINFO_COLOR or bitflags & __SQF.TEAMINFO_SCORE:
                for i in range(numteams):
                    if bitflags & __SQF.TEAMINFO_NAME:
                        team_name = bb.get_string_null_terminated()
                        print(i, " team's name:", team_name)
                    if bitflags & __SQF.TEAMINFO_COLOR:
                        team_color = bb.get_int()
                        print(i, " team's color:", team_color)
                    if bitflags & __SQF.TEAMINFO_SCORE:
                        team_score = bb.get_short()
                        print(i, " team's score:", team_score)
            if bitflags & __SQF.TESTING_SERVER:
                is_running_custom = bb.get_byte() > 0
                custom_binary_name = bb.get_string_null_terminated()
                print("Running custom =", is_running_custom, "[", custom_binary_name, "]")
            if bitflags & __SQF.DATA_MD5SUM:
                data_md5_sum = bb.get_string_null_terminated()
                print("MD5 sum:", data_md5_sum)
            if bitflags & __SQF.ALL_DMFLAGS:
                num_dm_flags = bb.get_byte()
                dmflaglist = [0, 0, 0, 0, 0]  # DMFlags, DMFlags2, DMFlags3, CompatFlags, CompatFlags2
                for flagindex in range(num_dm_flags):
                    dmflaglist[flagindex] = bb.get_int()
                print("DMFlag/CompatFlag list:", dmflaglist)
            if bitflags & __SQF.SECURITY_SETTINGS:
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
