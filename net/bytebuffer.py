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

from struct import pack, unpack


# A buffer class for bytes that are read in a FIFO pattern
# - For example, when sockets communicate a short and a long, you want to read
# the short first, and then the long... this class allows that
# - Any invalid operations for 'getters' (like not enough bytes in the buffer)
# will yield a ByteBufferException
class ByteBuffer:
    def __init__(self, is_little_endian_boolean):
        self._bytedata = []
        self._little_endian = is_little_endian_boolean

    def size(self):
        return len(self._bytedata)

    def clear(self):
        del self._bytedata
        self._bytedata = []

    def put_bytes(self, bytes_):
        self._bytedata.extend(bytes_)

    def put_byte(self, byte_):
        self._bytedata.append(byte_)

    def put_short(self, short_):
        data = pack("<h" if self._little_endian else ">h", short_)
        for b in data:
            self._bytedata.append(b)

    def put_short_unsigned(self, short_):
        data = pack("<H" if self._little_endian else ">H", short_)
        for b in data:
            self._bytedata.append(b)

    def put_int(self, int_):
        data = pack("<l" if self._little_endian else ">l", int_)
        for b in data:
            self._bytedata.append(b)

    def put_int_unsigned(self, int_):
        data = pack("<L" if self._little_endian else ">L", int_)
        for b in data:
            self._bytedata.append(b)

    def put_float(self, float_):
        data = pack("<f" if self._little_endian else ">f", float_)
        for b in data:
            self._bytedata.append(b)

    def put_long(self, long_):
        data = pack("<q" if self._little_endian else ">q", long_)
        for b in data:
            self._bytedata.append(b)

    def put_long_unsigned(self, long_):
        data = pack("<Q" if self._little_endian else ">Q", long_)
        for b in data:
            self._bytedata.append(b)

    def put_string(self, str_, encodetype='latin1', null_terminator=False):
        for b in str_.encode(encodetype):
            self._bytedata.append(b)
        if null_terminator:
            self._bytedata.append(0)

    def peek_front_byte(self):
        if len(self._bytedata) == 0:
            raise ByteBufferException("ByteBuffer is empty, cannot peek at a byte from an empty buffer.")
        return self._bytedata[0]

    def get_byte(self):
        if len(self._bytedata) == 0:
            raise ByteBufferException("ByteBuffer is empty, cannot get a byte from an empty buffer.")
        return self._bytedata.pop(0)

    def get_all_bytes(self):
        if len(self._bytedata) == 0:
            raise ByteBufferException("ByteBuffer is empty, cannot get all bytes from an empty buffer.")
        return_bytes = self._bytedata[:]  # Copy the bytes
        self._bytedata = []
        return return_bytes

    def get_short(self):
        if len(self._bytedata) < 2:
            raise ByteBufferException("Less than two bytes in the ByteBuffer, cannot extract a signed short.")
        data = bytearray()
        for i in range(2):
            data.append(self._bytedata.pop(0))
        return unpack("<h" if self._little_endian else ">h", bytes(data))[0]

    def get_short_unsigned(self):
        if len(self._bytedata) < 2:
            raise ByteBufferException("Less than two bytes in the ByteBuffer, cannot extract an unsigned short.")
        data = bytearray()
        for i in range(2):
            data.append(self._bytedata.pop(0))
        return unpack("<H" if self._little_endian else ">H", bytes(data))[0]

    def get_int(self):
        if len(self._bytedata) < 4:
            raise ByteBufferException("Less than four bytes in the ByteBuffer, cannot extract a signed int.")
        data = bytearray()
        for i in range(4):
            data.append(self._bytedata.pop(0))
        return unpack("<l" if self._little_endian else ">l", bytes(data))[0]

    def get_int_unsigned(self):
        if len(self._bytedata) < 4:
            raise ByteBufferException("Less than four bytes in the ByteBuffer, cannot extract an unsigned int.")
        data = bytearray()
        for i in range(4):
            data.append(self._bytedata.pop(0))
        return unpack("<L" if self._little_endian else ">L", bytes(data))[0]

    def get_float(self):
        if len(self._bytedata) < 4:
            raise ByteBufferException("Less than four bytes in the ByteBuffer, cannot extract a float.")
        data = bytearray()
        for i in range(4):
            data.append(self._bytedata.pop(0))
        return unpack("<f" if self._little_endian else ">f", bytes(data))[0]

    def get_long(self):
        if len(self._bytedata) < 8:
            raise ByteBufferException("Less than eight bytes in the ByteBuffer, cannot extract a signed long.")
        data = bytearray()
        for i in range(8):
            data.append(self._bytedata.pop(0))
        return unpack("<q" if self._little_endian else ">q", bytes(data))[0]

    def get_long_unsigned(self):
        if len(self._bytedata) < 8:
            raise ByteBufferException("Less than eight bytes in the ByteBuffer, cannot extract an unsigned long.")
        data = bytearray()
        for i in range(8):
            data.append(self._bytedata.pop(0))
        return unpack("<Q" if self._little_endian else ">Q", bytes(data))[0]

    def get_string(self, numchars, decoding='latin1'):
        if numchars > len(self._bytedata):
            raise ByteBufferException("Not enough bytes in the ByteBuffer to extract a string")
        rawdata = bytearray()
        for i in range(numchars):
            rawdata.append(self._bytedata.pop(0))
        return rawdata.decode(decoding)

    def get_string_null_terminated(self, decoding='latin1'):
        rawdata = bytearray()
        while True:
            if len(self._bytedata) == 0:
                raise ByteBufferException("Did not find null terminator before ByteBuffer reached the end of it's data")
            b = self._bytedata.pop(0)
            if b == 0:
                break
            rawdata.append(b)
        return rawdata.decode(decoding)


# Indicates something bad occured in the bytebuffer, like improper index or some overflow
class ByteBufferException(Exception):
    pass
