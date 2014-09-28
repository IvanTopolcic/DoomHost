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

import hashlib
from misc.enum import enum
import net.huffman
import socket


# Enumeration of different server rcon responses
__SVRC = enum(OLDPROTOCOL=32, BANNED=33, SALT=34, LOGGEDIN=35, INVALIDPASSWORD=36, MESSAGE=37, UPDATE=38)

# Enumeration of
__CLRC = enum(BEGINCONNECTION=52, PASSWORD=53, COMMAND=54, PONG=55, DISCONNECT=56)

# Enumeration of rcon updates
__SVRCU = enum(PLAYERDATA=0, ADMINCOUNT=1, MAP=2)

# Zan protocol version
__ZAN_PROTOCOL_VERSION = 3

# A quick lookup table for hex characters
__hex_lookup = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f')


# Converst a bytearray to a string
def __bytes_to_hexstring(bytearr):
    hexstring = ''
    for byte in bytearr:
        hexstring += __hex_lookup[(byte >> 4) & 0x0F]
        hexstring += __hex_lookup[byte & 0x0F]
    return hexstring


# Sends a command to the client, will raise an exception if it times out (10 sec)
# NOTE: This does blocking, move to its own thread in the future
def send_command(ip, port, rconpass, command):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Set the socket values
            s.setblocking(True)
            s.settimeout(5.0)

            # Create a byte array with the required headers
            rawdata = bytearray()
            rawdata.append(__CLRC.BEGINCONNECTION)
            rawdata.append(__ZAN_PROTOCOL_VERSION)
            encodeddata = net.huffman.encode(rawdata)
            s.sendto(encodeddata, (ip, port))

            # Wait for the response
            data, address = s.recvfrom(64)
            decodeddata = net.huffman.decode(data)
            if decodeddata[0] != __SVRC.SALT:
                print("Header not a salt:", decodeddata[0])
                return False

            # Extract the salt by tossing away header and null terminator
            saltdata = decodeddata[1:33]

            # To generate the login, concatenate the salt and password bytes
            logindata = bytearray()
            logindata.extend(saltdata)
            logindata.extend(rconpass.encode('ascii'))

            # Then hash the salt/pass combo
            md5 = hashlib.md5()
            md5.update(logindata)
            hashlogin = md5.digest()

            # Then convert into hex
            hashedhex = __bytes_to_hexstring(hashlogin)

            # Now send the password header + the payload
            hashedlogin = bytearray()
            hashedlogin.append(__CLRC.PASSWORD)
            hashedlogin.extend(hashedhex.encode('ascii'))

            # Encode and send
            encodedhashedlogin = net.huffman.encode(hashedlogin)
            s.sendto(encodedhashedlogin, (ip, port))

            # Wait for the response
            data, address = s.recvfrom(2048) # Hopefully this holds whatever is sent, though it should be < 576
            decodeddata = net.huffman.decode(data)
            if decodeddata[0] != __SVRC.LOGGEDIN:
                print("Failure logging in:", decodeddata[0])
                return False

            # Send our command now
            commandtosendbytes = bytearray()
            commandtosendbytes.append(__CLRC.COMMAND)
            commandtosendbytes.extend(command.encode('ascii'))
            encodedcommandtosend = net.huffman.encode(commandtosendbytes)
            s.sendto(encodedcommandtosend, (ip, port))
    except socket.timeout:
        print("Socket timed out attempting to send rcon command", command, "to", address, ":", port)
        return False
    return True
