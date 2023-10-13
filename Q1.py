def hex_to_bin_4bit(hex_digit):
    return format(int(hex_digit, 16), '04b')

def block_to_matrix(block):
    return [[block[0], block[2]], [block[1], block[3]]]

def matrix_to_block_hex(matrix):
    block_bin = matrix[0][0] + matrix[1][0] + matrix[0][1] + matrix[1][1]
    block_hex = hex(int(block_bin, 2))[2:].upper().zfill(4)
    return block_hex

def sub_nibbles(matrix):
    sbox = {
        '0000': '1010', '0001': '0000', '0010': '1001', '0011': '1110',
        '0100': '0110', '0101': '0011', '0110': '1111', '0111': '0101',
        '1000': '0001', '1001': '1101', '1010': '1100', '1011': '0111',
        '1100': '1011', '1101': '0100', '1110': '0010', '1111': '1000'
    }
    return [[sbox[matrix[0][0]], sbox[matrix[0][1]]], [sbox[matrix[1][0]], sbox[matrix[1][1]]]]

def shift_row(matrix):
    return [[matrix[0][1], matrix[0][0]], [matrix[1][0], matrix[1][1]]]

def generate_round_keys(key_matrix):
    Rcon1 = '1110'
    Rcon2 = '1010'
    w0, w1, w2, w3 = key_matrix[0][0], key_matrix[1][0], key_matrix[0][1], key_matrix[1][1]
    w4 = format(int(w0, 2) ^ int(sub_nibbles([[w3, '0000'], ['0000', '0000']])[0][0], 2) ^ int(Rcon1, 2), '04b')
    w5 = format(int(w1, 2) ^ int(w4, 2), '04b')
    w6 = format(int(w2, 2) ^ int(w5, 2), '04b')
    w7 = format(int(w3, 2) ^ int(w6, 2), '04b')
    K1 = [[w4, w6], [w5, w7]]
    w8 = format(int(w4, 2) ^ int(sub_nibbles([[w7, '0000'], ['0000', '0000']])[0][0], 2) ^ int(Rcon2, 2), '04b')
    w9 = format(int(w5, 2) ^ int(w8, 2), '04b')
    w10 = format(int(w6, 2) ^ int(w9, 2), '04b')
    w11 = format(int(w7, 2) ^ int(w10, 2), '04b')
    K2 = [[w8, w10], [w9, w11]]
    return K1, K2

def multiply_GF24(a, b):
    m = 0
    while b > 0:
        if b & 1:  # Least significant bit is 1
            m ^= a
        a <<= 1  # left shift
        if a & 0x10:  # Fourth bit is set, so we need to take it modulo the irreducible polynomial
            a ^= 0x13  # x^4 + x + 1 (10011 in binary)
        b >>= 1  # right shift
    return m & 0xF  # Only keep the last 4 bits

def mix_columns(matrix):
    d0 = multiply_GF24(int(matrix[0][0], 2), 1) ^ multiply_GF24(int(matrix[1][0], 2), 4)
    d1 = multiply_GF24(int(matrix[0][0], 2), 4) ^ multiply_GF24(int(matrix[1][0], 2), 1)
    d2 = multiply_GF24(int(matrix[0][1], 2), 1) ^ multiply_GF24(int(matrix[1][1], 2), 4)
    d3 = multiply_GF24(int(matrix[0][1], 2), 4) ^ multiply_GF24(int(matrix[1][1], 2), 1)
    return [[format(d0, '04b'), format(d2, '04b')], [format(d1, '04b'), format(d3, '04b')]]

# Main Program
text_block = input("Enter a text block (4 hex digits): ")
key = input("Enter a key (4 hex digits): ")

# Convert hex input to 4-bit binary strings
text_block = [hex_to_bin_4bit(x) for x in text_block]
key = [hex_to_bin_4bit(x) for x in key]

# Convert to 2x2 matrices
text_matrix = block_to_matrix(text_block)
key_matrix = block_to_matrix(key)

# Perform operations
result = sub_nibbles(text_matrix)
print(f"SubNibbles: {matrix_to_block_hex(result)}")

result = shift_row(text_matrix)
print(f"ShiftRow: {matrix_to_block_hex(result)}")

result = mix_columns(text_matrix)
print(f"MixColumns: {matrix_to_block_hex(result)}")

K1, K2 = generate_round_keys(key_matrix)
print(f"GenerateRoundKeys: K1 = {matrix_to_block_hex(K1)}, K2 = {matrix_to_block_hex(K2)}")
