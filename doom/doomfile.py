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
import struct
import re
import zipfile


# Reads a Doom file (wad, zip, pk3...etc), and gets the data needed from the
# file such as the map list and md5 hash.
# FUNCTIONS:
#    get_hash(): Gets the md5 hash of this wad (string of bytes)
#    get_maplist(): Gets a list of strings for all the maps, or an empty list
#                   if there is no maps
# EXCEPTIONS:
#    Constructor: - Will throw IOError/OSError/FileNotFoundError if it cannot
#                 read the file, BadZipfile if it's a pk3/pk7 and is corrupt
#                 - Will throw DoomFileError if the extension is wrong, or this
#                 cannot read the file due to it being corrupt
class DoomFile:
    def __init__(self, path):
        self.__maplist = []
        self.__md5 = b'\0'
        md5hasher = hashlib.md5()
        with open(path, 'rb') as f:
            data = md5hasher.update(f.read())
        self.__md5 = md5hasher.digest()
        self.__process_file(path)

    def get_hash(self):
        return self.__md5

    def get_maplist(self):
        return self.__maplist

    def __process_file(self, path):
        lowerpath = path.lower()
        if lowerpath.endswith(".wad"):
            self.__process_wad(path)
        elif lowerpath.endswith(".pk3"):
            self.__process_pk3(path)
        elif lowerpath.endswith(".pk7"):
            self.__process_pk7(path)
        else:
            raise DoomFileError("Unexpected file extension (not wad/pk3/pk7).")

    def __process_wad(self, path):
        lumpnames = []
        try:
            with open(path, 'rb') as f:
                headerdata = f.read(12)
                (headerid, numlumps, infotableoffset) = struct.unpack('<LLL', headerdata)
                if numlumps == 0:
                    return
                if infotableoffset < 0 or numlumps < 0:
                    raise DoomFileError("Corrupt header, negative offset/lump count found.")
                f.seek(infotableoffset)
                for index in range(numlumps):
                    lumpdata = f.read(16)
                    (filepos, size, name) = struct.unpack("<LL8s", lumpdata)
                    lumpnames.append(re.sub('\0', '', name.decode("ascii")))  # Use regex to replace nulls with nothing
        except:
            raise DoomFileError("Wad file is corrupt.")
        prevname = ''
        prevnamelower = ''
        for lumpname in lumpnames:
            lowerlumpname = lumpname.lower()
            if lowerlumpname in MAP_LUMP_NAMES:
                if prevnamelower not in MAP_LUMP_NAMES:
                    self.__maplist.append(prevname)
            prevname = lumpname
            prevnamelower = lowerlumpname

    def __process_pk3(self, path):
        pattern = re.compile("^maps/(\w+)\.wad")
        with zipfile.ZipFile(path, 'r') as zf:
            for name in zf.namelist():
                lowername = name.lower()
                match = re.search(pattern, name)
                if match:
                    self.__maplist.append(match.group(1))

    def __process_pk7(self, path):
        print("PK7 NOT SUPPORTED -- Attempting pk3 processing...")
        self.__process_pk3(path)  # Attempt to do process PK3


# An exception to be raised when something goes wrong processing a DoomFile
class DoomFileError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# A list of known map names
MAP_LUMP_NAMES = ('things', 'linedefs', 'sidedefs', 'vertexes', 'segs',
                  'ssectors', 'nodes', 'sectors', 'reject', 'blockmap',
                  'behavior', 'textmap', 'znodes', 'endmap', 'dialogue')
