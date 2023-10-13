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

def inv_sub_nibbles(matrix):
    sbox = {
        '1010': '0000', '0000': '0001', '1001': '0010', '1110': '0011',
    '0110': '0100', '0011': '0101', '1111': '0110', '0101': '0111',
    '0001': '1000', '1101': '1001', '1100': '1010', '0111': '1011',
    '1011': '1100', '0100': '1101', '0010': '1110', '1000': '1111'
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
    binary_matrix = [['1001', '0010'], ['0010', '1001']]  # The binary equivalents of 9 and 2
    mixcolumn_matrix = [[0, 0], [0, 0]]

    # Separate the columns
    column1 = [int(matrix[i][0], 2) for i in range(2)]
    column2 = [int(matrix[i][1], 2) for i in range(2)]

    # Calculate the new values for the first column
    for row in range(2):
        mixcolumn_matrix[row][0] = multiply_GF24(int(binary_matrix[row][0], 2), column1[0]) ^ multiply_GF24(int(binary_matrix[row][1], 2), column1[1])

    # Calculate the new values for the second column
    for row in range(2):
        mixcolumn_matrix[row][1] = multiply_GF24(int(binary_matrix[row][0], 2), column2[0]) ^ multiply_GF24(int(binary_matrix[row][1], 2), column2[1])

    # Convert to 4-bit binary format
    for i in range(2):
        for j in range(2):
            mixcolumn_matrix[i][j] = format(mixcolumn_matrix[i][j], '04b')

    return mixcolumn_matrix

def XOR_matrices(matrix1, matrix2):
    return [[format(int(matrix1[i][j], 2) ^ int(matrix2[i][j], 2), '04b') for j in range(len(matrix1[0]))] for i in range(len(matrix1))]

def decrypt_block(cipher_text_block, key_matrix, K1, K2):
    cipher_text_block = [hex_to_bin_4bit(x) for x in cipher_text_block]
    cipher_matrix = block_to_matrix(cipher_text_block)

    # Applying shift row on cipher text
    shiftrow1 = shift_row(cipher_matrix)

    # Adding round key K2
    k2_added_matrix = XOR_matrices(shiftrow1, K2)

    # Making subnibbles
    subnibbles1 = inv_sub_nibbles(k2_added_matrix)

    # Shifting Row again
    shiftrow2 = shift_row(subnibbles1)

    # Calculating mix columns
    mixcolumn_matrix = mix_columns(shiftrow2)

    # Adding round key K1
    k1_added_matrix = XOR_matrices(mixcolumn_matrix, K1)

    # Making subnibbles again for the final step
    plain_text = inv_sub_nibbles(k1_added_matrix)
    return matrix_to_block_hex(plain_text)

def main_decryption_program():
    # Read the encrypted content from "secret.txt"
    print("Reading encrypted file secret.txt...")
    with open("secret.txt", "r") as f: # --> change path XD
        encrypted_text = f.read().strip().replace(" ", "").replace("\n", "")
        encrypted_blocks = [encrypted_text[i:i+4] for i in range(0, len(encrypted_text), 4)]

    # Get the decryption key from the user
    key = input("Enter the decryption key (4 hex digits): ")

    # Prepare the key matrix
    key = [hex_to_bin_4bit(x) for x in key]
    key_matrix = block_to_matrix(key)

    # Generate round keys
    K1, K2 = generate_round_keys(key_matrix)\

    # Decrypt the content block by block
    decrypted_blocks = []
    for block in encrypted_blocks:
        decrypted_block = decrypt_block(block, key_matrix, K1, K2)
        decrypted_blocks.append(decrypted_block)

    decrypted_text = "".join([chr(int(block[i:i+2], 16)) for block in decrypted_blocks for i in (0, 2)])
    print("Decrypted Result")
    print("--------------------")
    print(decrypted_text)

if __name__ == "__main__":
    main_decryption_program()
