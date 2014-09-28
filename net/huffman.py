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

# The huffman values compatible with Zandronum/Skulltag
# - Bitcodes are least signifant from the left, this way it's possible to
# iterate through them from the beginning.
# - How this works is that you start from the root node each time and work your
# way down the tree. When you get to the bottom, that node is the index. For
# example, if index 0 is "010", you'd read the first char which is 0, and go
# left (or create a node if there is none), then read index 1 which is 1, and
# go right (or create a node if there is none), and repeat until the end. For
# the last digit, that is where you will make the child node which will have
# inside it the byte index.
__huffman_compatible_bitcodes = (
    "010",  # 2 [Index: 0]
    "110111",  # 55 [Index: 1]
    "101110010",  # 370 [Index: 2]
    "00100",  # 4 [Index: 3]
    "10011011",  # 155 [Index: 4]
    "00101",  # 5 [Index: 5]
    "100110101",  # 309 [Index: 6]
    "100001100",  # 268 [Index: 7]
    "100101100",  # 300 [Index: 8]
    "001110100",  # 116 [Index: 9]
    "011001001",  # 201 [Index: 10]
    "11001000",  # 200 [Index: 11]
    "101100001",  # 353 [Index: 12]
    "100100111",  # 295 [Index: 13]
    "001111111",  # 127 [Index: 14]
    "101110000",  # 368 [Index: 15]
    "101110001",  # 369 [Index: 16]
    "001111011",  # 123 [Index: 17]
    "11011011",  # 219 [Index: 18]
    "101111100",  # 380 [Index: 19]
    "100001110",  # 270 [Index: 20]
    "110011111",  # 415 [Index: 21]
    "101100000",  # 352 [Index: 22]
    "001111100",  # 124 [Index: 23]
    "0011000",  # 24 [Index: 24]
    "001111000",  # 120 [Index: 25]
    "10001100",  # 140 [Index: 26]
    "100101011",  # 299 [Index: 27]
    "100010000",  # 272 [Index: 28]
    "101111011",  # 379 [Index: 29]
    "100100110",  # 294 [Index: 30]
    "100110010",  # 306 [Index: 31]
    "0111",  # 7 [Index: 32]
    "1111000",  # 120 [Index: 33]
    "00010001",  # 17 [Index: 34]
    "00011010",  # 26 [Index: 35]
    "00011000",  # 24 [Index: 36]
    "00010101",  # 21 [Index: 37]
    "00010000",  # 16 [Index: 38]
    "00110111",  # 55 [Index: 39]
    "00110110",  # 54 [Index: 40]
    "00011100",  # 28 [Index: 41]
    "01100101",  # 101 [Index: 42]
    "1101001",  # 105 [Index: 43]
    "00110100",  # 52 [Index: 44]
    "10110011",  # 179 [Index: 45]
    "10110100",  # 180 [Index: 46]
    "1111011",  # 123 [Index: 47]
    "10111100",  # 188 [Index: 48]
    "10111010",  # 186 [Index: 49]
    "11001001",  # 201 [Index: 50]
    "11010101",  # 213 [Index: 51]
    "11111110",  # 254 [Index: 52]
    "11111100",  # 252 [Index: 53]
    "10001110",  # 142 [Index: 54]
    "11110011",  # 243 [Index: 55]
    "001101011",  # 107 [Index: 56]
    "10000000",  # 128 [Index: 57]
    "000101101",  # 45 [Index: 58]
    "11010000",  # 208 [Index: 59]
    "001110111",  # 119 [Index: 60]
    "100000010",  # 258 [Index: 61]
    "11100111",  # 231 [Index: 62]
    "001100101",  # 101 [Index: 63]
    "11100110",  # 230 [Index: 64]
    "00111001",  # 57 [Index: 65]
    "10001010",  # 138 [Index: 66]
    "00010011",  # 19 [Index: 67]
    "001110110",  # 118 [Index: 68]
    "10001111",  # 143 [Index: 69]
    "000111110",  # 62 [Index: 70]
    "11000111",  # 199 [Index: 71]
    "11010111",  # 215 [Index: 72]
    "11100011",  # 227 [Index: 73]
    "000101000",  # 40 [Index: 74]
    "001100111",  # 103 [Index: 75]
    "11010100",  # 212 [Index: 76]
    "000111010",  # 58 [Index: 77]
    "10010111",  # 151 [Index: 78]
    "100000111",  # 263 [Index: 79]
    "000100100",  # 36 [Index: 80]
    "001110001",  # 113 [Index: 81]
    "11111010",  # 250 [Index: 82]
    "100100011",  # 291 [Index: 83]
    "11110100",  # 244 [Index: 84]
    "000110111",  # 55 [Index: 85]
    "001111010",  # 122 [Index: 86]
    "100010011",  # 275 [Index: 87]
    "100110001",  # 305 [Index: 88]
    "11101",  # 29 [Index: 89]
    "110001011",  # 395 [Index: 90]
    "101110110",  # 374 [Index: 91]
    "101111110",  # 382 [Index: 92]
    "100100010",  # 290 [Index: 93]
    "100101001",  # 297 [Index: 94]
    "01101",  # 13 [Index: 95]
    "100100100",  # 292 [Index: 96]
    "101100101",  # 357 [Index: 97]
    "110100011",  # 419 [Index: 98]
    "100111100",  # 316 [Index: 99]
    "110110001",  # 433 [Index: 100]
    "100010010",  # 274 [Index: 101]
    "101101101",  # 365 [Index: 102]
    "011001110",  # 206 [Index: 103]
    "011001101",  # 205 [Index: 104]
    "11111101",  # 253 [Index: 105]
    "100010001",  # 273 [Index: 106]
    "100110000",  # 304 [Index: 107]
    "110001000",  # 392 [Index: 108]
    "110110000",  # 432 [Index: 109]
    "0001001010",  # 74 [Index: 110]
    "110001010",  # 394 [Index: 111]
    "101101010",  # 362 [Index: 112]
    "000110110",  # 54 [Index: 113]
    "10110001",  # 177 [Index: 114]
    "110001101",  # 397 [Index: 115]
    "110101101",  # 429 [Index: 116]
    "110001100",  # 396 [Index: 117]
    "000111111",  # 63 [Index: 118]
    "110010101",  # 405 [Index: 119]
    "111000100",  # 452 [Index: 120]
    "11011001",  # 217 [Index: 121]
    "110010110",  # 406 [Index: 122]
    "110011110",  # 414 [Index: 123]
    "000101100",  # 44 [Index: 124]
    "001110101",  # 117 [Index: 125]
    "101111101",  # 381 [Index: 126]
    "1001110",  # 78 [Index: 127]
    "0000",  # 0 [Index: 128]
    "1000010",  # 66 [Index: 129]
    "0001110111",  # 119 [Index: 130]
    "0001100101",  # 101 [Index: 131]
    "1010",  # 10 [Index: 132]
    "11001110",  # 206 [Index: 133]
    "0110011000",  # 408 [Index: 134]
    "0110011001",  # 409 [Index: 135]
    "1000011011",  # 539 [Index: 136]
    "1001100110",  # 614 [Index: 137]
    "0011110011",  # 243 [Index: 138]
    "0011001100",  # 204 [Index: 139]
    "11111001",  # 249 [Index: 140]
    "0110010001",  # 401 [Index: 141]
    "0001010011",  # 83 [Index: 142]
    "1000011010",  # 538 [Index: 143]
    "0001001011",  # 75 [Index: 144]
    "1001101001",  # 617 [Index: 145]
    "101110111",  # 375 [Index: 146]
    "1000001101",  # 525 [Index: 147]
    "1000011111",  # 543 [Index: 148]
    "1100000101",  # 773 [Index: 149]
    "0110000010",  # 386 [Index: 150]
    "1011011101",  # 733 [Index: 151]
    "11110101",  # 245 [Index: 152]
    "0001111011",  # 123 [Index: 153]
    "1101000101",  # 837 [Index: 154]
    "1101000100",  # 836 [Index: 155]
    "1001000010",  # 578 [Index: 156]
    "0110000011",  # 387 [Index: 157]
    "1011001000",  # 712 [Index: 158]
    "100101010",  # 298 [Index: 159]
    "1100110",  # 102 [Index: 160]
    "111100101",  # 485 [Index: 161]
    "1100101111",  # 815 [Index: 162]
    "0001100111",  # 103 [Index: 163]
    "1110000",  # 112 [Index: 164]
    "0011111100",  # 252 [Index: 165]
    "11111011",  # 251 [Index: 166]
    "1100101110",  # 814 [Index: 167]
    "101110011",  # 371 [Index: 168]
    "1001100111",  # 615 [Index: 169]
    "1001111111",  # 639 [Index: 170]
    "1011011100",  # 732 [Index: 171]
    "111110001",  # 497 [Index: 172]
    "101111010",  # 378 [Index: 173]
    "1011010110",  # 726 [Index: 174]
    "1001010000",  # 592 [Index: 175]
    "1001000011",  # 579 [Index: 176]
    "1001111110",  # 638 [Index: 177]
    "0011111011",  # 251 [Index: 178]
    "1000011110",  # 542 [Index: 179]
    "1000101100",  # 556 [Index: 180]
    "01100001",  # 97 [Index: 181]
    "00010111",  # 23 [Index: 182]
    "1000000110",  # 518 [Index: 183]
    "110000101",  # 389 [Index: 184]
    "0001111010",  # 122 [Index: 185]
    "0011001101",  # 205 [Index: 186]
    "0110011110",  # 414 [Index: 187]
    "110010100",  # 404 [Index: 188]
    "111000101",  # 453 [Index: 189]
    "0011001001",  # 201 [Index: 190]
    "0011110010",  # 242 [Index: 191]
    "110000001",  # 385 [Index: 192]
    "101101111",  # 367 [Index: 193]
    "0011111101",  # 253 [Index: 194]
    "110110100",  # 436 [Index: 195]
    "11100100",  # 228 [Index: 196]
    "1011001001",  # 713 [Index: 197]
    "0011001000",  # 200 [Index: 198]
    "0001110110",  # 118 [Index: 199]
    "111111111",  # 511 [Index: 200]
    "110101100",  # 428 [Index: 201]
    "111111110",  # 510 [Index: 202]
    "1000001011",  # 523 [Index: 203]
    "1001011010",  # 602 [Index: 204]
    "110000000",  # 384 [Index: 205]
    "000111100",  # 60 [Index: 206]
    "111110000",  # 496 [Index: 207]
    "011000000",  # 192 [Index: 208]
    "1001111010",  # 634 [Index: 209]
    "111001011",  # 459 [Index: 210]
    "011000111",  # 199 [Index: 211]
    "1001000001",  # 577 [Index: 212]
    "1001111100",  # 636 [Index: 213]
    "1000110111",  # 567 [Index: 214]
    "1001101000",  # 616 [Index: 215]
    "0110001100",  # 396 [Index: 216]
    "1001111011",  # 635 [Index: 217]
    "0011010101",  # 213 [Index: 218]
    "1000101101",  # 557 [Index: 219]
    "0011111010",  # 250 [Index: 220]
    "0001100100",  # 100 [Index: 221]
    "01100010",  # 98 [Index: 222]
    "110000100",  # 388 [Index: 223]
    "101101100",  # 364 [Index: 224]
    "0110011111",  # 415 [Index: 225]
    "1001011011",  # 603 [Index: 226]
    "1000101110",  # 558 [Index: 227]
    "111100100",  # 484 [Index: 228]
    "1000110110",  # 566 [Index: 229]
    "0110001101",  # 397 [Index: 230]
    "1001000000",  # 576 [Index: 231]
    "110110101",  # 437 [Index: 232]
    "1000001000",  # 520 [Index: 233]
    "1000001001",  # 521 [Index: 234]
    "1100000100",  # 772 [Index: 235]
    "110001001",  # 393 [Index: 236]
    "1000000111",  # 519 [Index: 237]
    "1001111101",  # 637 [Index: 238]
    "111001010",  # 458 [Index: 239]
    "0011010100",  # 212 [Index: 240]
    "1000101111",  # 559 [Index: 241]
    "101111111",  # 383 [Index: 242]
    "0001010010",  # 82 [Index: 243]
    "0011100000",  # 224 [Index: 244]
    "0001100110",  # 102 [Index: 245]
    "1000001010",  # 522 [Index: 246]
    "0011100001",  # 225 [Index: 247]
    "11000011",  # 195 [Index: 248]
    "1011010111",  # 727 [Index: 249]
    "1000001100",  # 524 [Index: 250]
    "100011010",  # 282 [Index: 251]
    "0110010000",  # 400 [Index: 252]
    "100100101",  # 293 [Index: 253]
    "1001010001",  # 593 [Index: 254]
    "110000011"  # 387 [Index: 255]
)


# A POD for the huffman node
class HuffmanNode:
    def __init__(self):
        self.byteindex = -1
        self.bitcode = []
        self.children = [None, None]


# The root node for decoding
__rootnode = HuffmanNode()

# A list of the encoding nodes
__encodingnodes = []

# A list of masks used for selecting bits
__huffman_bitmasks = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80)

# Checks if the module was initialized
__is_initialized = False


# Initializes the huffman table (NOTE: Do this with __init__ later)
def __init_huffman():
    # For each bytenum index with it's string representation
    for bytenum, bitcodestring in enumerate(__huffman_compatible_bitcodes):
        node = __rootnode
        # For each 0 and 1 in the string format
        for bitindex, bitvalue in enumerate(bitcodestring):
            # Get the direction to go based on the string
            nodeindex = int(bitvalue)
            # If there's no child, make one
            if node.children[nodeindex] is None:
                node.children[nodeindex] = HuffmanNode()
            node = node.children[nodeindex]
            # If we're at the end of the bit string, we need to finish adding the node
            if bitindex == len(bitcodestring) - 1:
                for c in bitcodestring:
                    node.bitcode.append(int(c))
                node.byteindex = bytenum
                __encodingnodes.append(node)
                break


def bindump(rawbytes):
    bits = []
    for byte in rawbytes:
        for i in range(8):
            if byte & __huffman_bitmasks[i] > 0:
                bits.append(1)
            else:
                bits.append(0)
    return bits


# Encodes the data and returns the encoded bytes
# This probably can be optimized
def encode(rawdata):
    # If the length is not correct, return an empty byte array
    if len(rawdata) <= 0:
        return bytearray()

    # Put all the bits as their own int into a list
    bits = []
    for b in rawdata:
        bitcode = __encodingnodes[b].bitcode
        for bit in bitcode:
            bits.append(bit)

    # If the list exceeds the default size, return the unencoded version
    if (len(bits) / 8) + 1 >= len(rawdata):
        encodeddata = bytearray(1)
        encodeddata[0] = 0xFF  # Compatibility issues with Zan/ST
        encodeddata.extend(rawdata)
        return encodeddata

    # Turn that list into an actual byte array
    residualbits = 8 - (len(bits) % 8)
    if residualbits == 8:
        residualbits = 0
    encodeddata = bytearray(1)
    encodeddata[0] = residualbits
    bitindex = 0
    byteindex = 0
    for bit in bits:
        if bitindex % 8 == 0:
            encodeddata.append(0)
            byteindex += 1
        # If the bit is set, OR the bitmask to the byte
        if bit == 1:
            encodeddata[byteindex] |= __huffman_bitmasks[bitindex]
        bitindex += 1
        bitindex %= 8
    return encodeddata


# Decodes the encoded data
def decode(encodeddata):
    # If the length is not correct, return an empty byte array
    if len(encodeddata) <= 0:
        return bytearray()

    # If the header is 0xFF, remove that and return the list
    if encodeddata[0] == 0xFF:
        removedheader = bytearray(encodeddata)
        removedheader.pop(0)
        return removedheader

    # Decode the data since it's encoded
    node = __rootnode
    decodeddata = bytearray()
    for bitindex in range(((len(encodeddata) - 1) * 8) - encodeddata[0]):
        byte = encodeddata[(bitindex // 8) + 1]  # Need to add + 1 to ignore the header byte
        bit = int(not not (byte & __huffman_bitmasks[bitindex % 8]))  # C/C++ trick to convert a num to either 0 or 1
        node = node.children[bit]
        if node.byteindex != -1:
            decodeddata.append(node.byteindex)
            node = __rootnode
    return decodeddata


# Initialize huffman if it's not working already
if not __is_initialized:
    __init_huffman()
    __is_initialized = True
